"""Forms for comments, contact inquiries, reader accounts, and blog posts."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import BlogPost, Comment, ContactInquiry

User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["name", "email", "body", "parent"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Your name"),
                                           "class": "field-input"}),
            "email": forms.EmailInput(attrs={"placeholder": _("Email (not published)"),
                                             "class": "field-input"}),
            "body": forms.Textarea(attrs={"placeholder": _("Join the conversation…"),
                                          "rows": 3, "class": "field-input"}),
            "parent": forms.HiddenInput(),
        }

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if len(body) < 3:
            raise forms.ValidationError(_("Comment is too short."))
        return body


class ContactForm(forms.ModelForm):
    # Honeypot: real users leave this blank; bots tend to fill every field.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactInquiry
        fields = ["name", "email", "department", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field-input"}),
            "email": forms.EmailInput(attrs={"class": "field-input"}),
            "department": forms.Select(attrs={"class": "field-input"}),
            "subject": forms.TextInput(attrs={"class": "field-input"}),
            "message": forms.Textarea(attrs={"class": "field-input", "rows": 6}),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""


class SignUpForm(UserCreationForm):
    """Registration form for readers who want to write blog posts.

    Wraps Django's own UserCreationForm (real password hashing,
    validation against AUTH_PASSWORD_VALIDATORS) and adds a required,
    unique email address.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "field-input", "placeholder": _("you@example.com"),
            "autocomplete": "email",
        }),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "field-input", "placeholder": _("Choose a username"),
            "autocomplete": "username",
        })
        self.fields["password1"].widget.attrs.update({
            "class": "field-input", "placeholder": _("Password"),
            "autocomplete": "new-password",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "field-input", "placeholder": _("Confirm password"),
            "autocomplete": "new-password",
        })
        for field in self.fields.values():
            field.help_text = ""  # keep the form compact; defaults are shown as placeholders

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("An account with that email already exists."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class BlogPostForm(forms.ModelForm):
    """Create/edit form for reader blog posts.

    Direction (ltr/rtl) is detected and stored automatically by
    BlogPost.save() — this form only collects the title and content
    a reader actually writes.
    """

    class Meta:
        model = BlogPost
        fields = ["title", "content"]
        widgets = {
            # Default auto-generated ids (id_title / id_content) are kept
            # deliberately — static/js/direction.js binds to them by id.
            "title": forms.TextInput(attrs={
                "class": "field-input",
                "placeholder": _("Give your post a title — عنوان لکھیں"),
                "autocomplete": "off",
            }),
            "content": forms.Textarea(attrs={
                "class": "field-input", "rows": 8,
                "placeholder": _("Write your story here, in English or Urdu… اپنی کہانی یہاں لکھیں"),
            }),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError(_("Title is required."))
        return title

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if not content:
            raise forms.ValidationError(_("Content is required."))
        return content

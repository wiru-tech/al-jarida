"""Data models for AL-JARIDA news portal."""
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .direction import detect_direction

# ---------------------------------------------------------------
# Section stock photography
#
# Last-resort artwork for an article that carries neither an uploaded
# image nor a featured_image_url — see Article.image_src. Keyed by
# Category.Kind so the substitute at least belongs to the right section.
#
# These are hotlinked from the Unsplash image CDN (free to use, no
# attribution required, no API key needed) rather than checked into the
# repo, which keeps the source tree free of binaries. The `w`/`q`/`fm`
# query string is Unsplash's own transform API — it serves a resized,
# re-encoded copy, so a card doesn't pull down a 4000px original.
# ---------------------------------------------------------------
_UNSPLASH = "https://images.unsplash.com/{}?w=1200&q=70&fm=jpg&auto=format&fit=crop"

CATEGORY_IMAGES = {
    "national":      _UNSPLASH.format("photo-1762246433142-d7d357c76cb5"),
    "international": _UNSPLASH.format("photo-1633095975779-fd354aa0dc95"),
    "world":         _UNSPLASH.format("photo-1633095975779-fd354aa0dc95"),
    "sports":        _UNSPLASH.format("photo-1569863959165-56dae551d4fc"),
    "technology":    _UNSPLASH.format("photo-1587845323226-bad89242c735"),
    "health":        _UNSPLASH.format("photo-1688565631550-ff8aa569f71a"),
    "entertainment": _UNSPLASH.format("photo-1657208431551-cbf415b8ef26"),
    "opinion":       _UNSPLASH.format("photo-1498644035638-2c3357894b10"),
    "islamic":       _UNSPLASH.format("photo-1558114965-eeb97aa84c3b"),
    "default":       _UNSPLASH.format("photo-1498644035638-2c3357894b10"),
}


class TimeStamped(models.Model):
    """Abstract base adding created/updated bookkeeping to every model."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStamped):
    """A top-level section such as National, Sports, Islamic Content."""

    class Kind(models.TextChoices):
        NATIONAL = "national", _("National News")
        INTERNATIONAL = "international", _("International News")
        SPORTS = "sports", _("Sports")
        TECH = "technology", _("Technology")
        HEALTH = "health", _("Health")
        ENTERTAINMENT = "entertainment", _("Entertainment")
        OPINION = "opinion", _("Opinion / Editorial")
        ISLAMIC = "islamic", _("Islamic Content")
        WORLD = "world", _("World")

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.NATIONAL)
    description = models.CharField(max_length=240, blank=True)
    accent_color = models.CharField(
        max_length=7, default="#b41d11",
        help_text=_("Hex accent used for the category label, e.g. #b41d11"),
    )
    order = models.PositiveSmallIntegerField(default=0, help_text=_("Menu sort order"))
    show_in_nav = models.BooleanField(default=True)
    show_on_home = models.BooleanField(
        default=False,
        help_text=_("Feature this category as its own section grid on the homepage."),
    )

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news:category", args=[self.slug])

    @property
    def is_islamic(self):
        return self.kind == self.Kind.ISLAMIC


class Tag(TimeStamped):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news:tag", args=[self.slug])


class Author(TimeStamped):
    """Editorial byline profile, optionally linked to a login account."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="author_profile",
    )
    display_name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True,
                            help_text=_("e.g. Senior Political Correspondent"))
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="authors/", blank=True, null=True)

    def __str__(self):
        return self.display_name


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Article.Status.PUBLISHED,
                           publish_at__lte=timezone.now())

    def with_relations(self):
        # Performance: pull FK + M2M in bounded queries.
        return self.select_related("category", "author").prefetch_related("tags")


class Article(TimeStamped):
    """A news article. Supports scheduling, multilingual bodies and media."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SCHEDULED = "scheduled", _("Scheduled")
        PUBLISHED = "published", _("Published")

    class Language(models.TextChoices):
        EN = "en", _("English")
        UR = "ur", _("Urdu")
        AR = "ar", _("Arabic")

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    kicker = models.CharField(max_length=80, blank=True,
                              help_text=_("Small overline label, e.g. GLOBAL AFFAIRS"))
    excerpt = models.TextField(max_length=400, blank=True)
    body = RichTextUploadingField(
        help_text=_("Main article text. Use the toolbar to format text and insert images."))
    body_secondary = models.TextField(
        blank=True,
        help_text=_("Optional pull-quote or block in a second language (Urdu/Arabic)."),
    )
    secondary_language = models.CharField(
        max_length=2, choices=Language.choices, blank=True,
        help_text=_("Language of the secondary block, drives RTL rendering."),
    )

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="articles")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True,
                               blank=True, related_name="articles")
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.EN)

    featured_image = models.ImageField(upload_to="articles/", blank=True, null=True)
    featured_image_url = models.URLField(
        blank=True, help_text=_("Fallback external image URL (used in the demo)."))
    image_caption = models.CharField(max_length=200, blank=True)

    video_embed_url = models.URLField(blank=True, help_text=_("YouTube/Vimeo embed URL"))
    video_file = models.FileField(
        upload_to="articles/videos/", blank=True, null=True,
        help_text=_("Optional self-hosted video upload (mp4/webm) — used if no embed URL is set."))

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField(default=False, help_text=_("Show in hero slot"))
    is_breaking = models.BooleanField(default=False, help_text=_("Show in breaking ticker"))
    publish_at = models.DateTimeField(default=timezone.now,
                                      help_text=_("Schedule future date/time here"))

    read_minutes = models.PositiveSmallIntegerField(default=4)
    view_count = models.PositiveIntegerField(default=0, editable=False)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-publish_at"]
        indexes = [
            models.Index(fields=["status", "publish_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:230] or "article"
            slug, n = base, 2
            while Article.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news:article", args=[self.slug])

    @property
    def is_live(self):
        return (self.status == self.Status.PUBLISHED
                and self.publish_at <= timezone.now())

    @property
    def is_rtl(self):
        return self.language in ("ur", "ar")

    @property
    def image_src(self):
        """The picture to render for this article — never empty.

        Order of preference: an image the newsroom uploaded, then the
        external web image URL on the record, then a category-appropriate
        stock photograph from CATEGORY_IMAGES.

        The last step is the point of this property. Every card, result
        row and related-stories tile on the site reserves a 16/9 box for
        the picture, so an article with no image of its own doesn't render
        smaller — it renders as a grey hole in the middle of a grid. The
        fallback is keyed on the category so a story published in a hurry
        still gets a photograph that at least belongs to its section.
        """
        if self.featured_image:
            return self.featured_image.url
        if self.featured_image_url:
            return self.featured_image_url
        return CATEGORY_IMAGES.get(self.category.kind, CATEGORY_IMAGES["default"])

    @property
    def paragraphs(self):
        return [p.strip() for p in self.body.split("\n") if p.strip()]

    @property
    def body_html(self):
        """Safe HTML for template rendering.

        Rich-text bodies authored via CKEditor already contain markup, so
        they're passed through as-is. Legacy plain-text bodies (no tags —
        e.g. pre-CKEditor seed data) are escaped and split into <p> blocks
        so old content keeps rendering with paragraph breaks.
        """
        text = self.body or ""
        if "<" in text and ">" in text:
            return mark_safe(text)
        return mark_safe("".join(f"<p>{escape(p)}</p>" for p in self.paragraphs))

    def register_view(self):
        """Record one open of this article.

        This counter is what ranks the homepage Trending rail and the
        Most Read widgets, so it has to be exact under concurrency: the
        increment is done as an atomic UPDATE rather than a read-then-save,
        which would lose opens whenever two readers land on the same story
        at once.

        The in-memory instance is then advanced to match, so a template
        rendering this object right after the call shows the count
        including the current open rather than the pre-increment value.
        """
        Article.objects.filter(pk=self.pk).update(view_count=F("view_count") + 1)
        self.view_count += 1


class GalleryImage(TimeStamped):
    """Photo-gallery item attached to an article."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="gallery/", blank=True, null=True)
    image_url = models.URLField(blank=True)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Image for {self.article.title}"

    @property
    def src(self):
        return self.image.url if self.image else self.image_url


class Comment(TimeStamped):
    """Reader comment with moderation workflow and threaded replies."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", null=True, blank=True,
                               on_delete=models.CASCADE, related_name="replies")
    name = models.CharField(max_length=80)
    email = models.EmailField(blank=True)
    body = models.TextField(max_length=1500)
    is_approved = models.BooleanField(default=False)
    likes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name} on {self.article}"


class MarketRate(TimeStamped):
    """Currency / market pair for the Markets & Currency widget."""
    pair = models.CharField(max_length=20, help_text=_("e.g. USD / EUR"))
    rate = models.DecimalField(max_digits=12, decimal_places=4)
    change_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                     help_text=_("Percentage change, may be negative"))
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.pair} {self.rate}"

    @property
    def direction(self):
        if self.change_pct > 0:
            return "up"
        if self.change_pct < 0:
            return "down"
        return "flat"


class WidgetData(TimeStamped):
    """
    Generic key/value widget store for schedules, quotes, horoscopes, profiles.
    Keeping this flexible lets the newsroom add widget content without code changes.
    """
    class Kind(models.TextChoices):
        TRANSPORT = "transport", _("Transport Schedule")
        QUOTE = "quote", _("Daily Quote")
        HOROSCOPE = "horoscope", _("Horoscope")
        PROFILE = "profile", _("Daily Profile")
        LIVE_TV = "live_tv", _("Live TV Stream")
        ISLAMIC = "islamic", _("Islamic Content (Hadith / Ayat)")

    kind = models.CharField(max_length=20, choices=Kind.choices)
    title = models.CharField(max_length=140)
    subtitle = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    meta = models.JSONField(default=dict, blank=True,
                            help_text=_("Structured payload, e.g. schedule rows or stream URL"))
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["kind", "order"]

    def __str__(self):
        return f"{self.get_kind_display()}: {self.title}"


class BlogPost(TimeStamped):
    """A short-form post written by a signed-in reader.

    Deliberately separate from the newsroom's editorial ``Article``
    model (which requires a Category, an Author profile, CKEditor body,
    etc.) — this is the lightweight "sign up, write, publish" flow for
    ordinary registered readers, with a plain title/content pair and
    per-field auto-detected text direction so a post can mix an
    English title with Urdu content (or vice-versa) and still render
    correctly.
    """

    class Direction(models.TextChoices):
        LTR = "ltr", _("Left-to-right")
        RTL = "rtl", _("Right-to-left")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="blog_posts",
    )
    title = models.CharField(max_length=220)
    content = models.TextField()

    # Auto-computed on every save from the text actually typed — not
    # user-editable, so it can never drift from the real content.
    title_dir = models.CharField(
        max_length=3, choices=Direction.choices, default=Direction.LTR,
        editable=False,
    )
    content_dir = models.CharField(
        max_length=3, choices=Direction.choices, default=Direction.LTR,
        editable=False,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title_dir = detect_direction(self.title)
        self.content_dir = detect_direction(self.content)
        super().save(*args, **kwargs)

    @property
    def author_name(self):
        return self.author.get_full_name() or self.author.username


class ContactInquiry(TimeStamped):
    """Submissions from the Contact & Inquiries form."""
    class Dept(models.TextChoices):
        FEEDBACK = "feedback", _("Feedback")
        PRESS = "press", _("Press")
        ADVERTISING = "advertising", _("Advertising")

    name = models.CharField(max_length=120)
    email = models.EmailField()
    department = models.CharField(max_length=20, choices=Dept.choices, default=Dept.FEEDBACK)
    subject = models.CharField(max_length=160)
    message = models.TextField(max_length=3000)
    is_handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "contact inquiries"

    def __str__(self):
        return f"{self.get_department_display()} — {self.subject}"

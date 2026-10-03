"""Views for AL-JARIDA."""
import json

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from .forms import BlogPostForm, CommentForm, ContactForm, SignUpForm
from .models import Article, BlogPost, Category, WidgetData

# Related-stories row below an article. Matches the three-column card grid
# it renders into, so the row is never left with a hole in it.
RELATED_COUNT = 3


def home(request):
    published = Article.objects.published().with_relations()

    hero = published.filter(is_featured=True).first() or published.first()

    # Powers the Trending / Breaking News rail beside the hero story.
    # Ranked by how many times each story has actually been opened
    # (Article.view_count, incremented once per article_detail request) —
    # not by recency, which is what `latest` below is for. `-publish_at`
    # is only a tiebreak so two stories on the same count still order
    # deterministically instead of shuffling between page loads.
    trending = (published.exclude(pk=getattr(hero, "pk", None))
                .order_by("-view_count", "-publish_at")[:5])

    latest = published.exclude(pk=getattr(hero, "pk", None))[:6]

    # The Islamic section gets its own hand-styled layout below, but its
    # heading/copy and which articles feed it come straight from whichever
    # Category an editor has tagged as Kind.ISLAMIC — never hardcoded here.
    islamic_category = Category.objects.filter(kind=Category.Kind.ISLAMIC).first()
    islamic = (published.filter(category=islamic_category)[:3]
               if islamic_category else published.none())

    # Section grids for the rest of the homepage body — entirely driven by
    # Category.show_on_home, so an editor adds/removes/reorders sections
    # (World, Business, a brand-new category, ...) from the admin with no
    # code change required.
    sections = []
    home_categories = Category.objects.filter(show_on_home=True)
    if islamic_category:
        home_categories = home_categories.exclude(pk=islamic_category.pk)
    for cat in home_categories:
        items = published.filter(category=cat)[:3]
        if items:
            sections.append({"category": cat, "articles": items})

    context = {
        "hero": hero,
        "trending": trending,
        "latest": latest,
        "islamic_category": islamic_category,
        "islamic_articles": islamic,
        "sections": sections,
    }
    return render(request, "news/home.html", context)


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.with_relations().prefetch_related("gallery", "comments"),
        slug=slug,
    )
    # Only editors may preview unpublished pieces.
    if not article.is_live and not request.user.is_staff:
        from django.http import Http404
        raise Http404()

    article.register_view()

    comments = article.comments.filter(is_approved=True, parent__isnull=True)
    form = CommentForm()

    # Related stories are rendered as full cards *below* the article, so a
    # short row (one lonely card in a three-up grid) looks broken. Same
    # category first — that's what makes them "related" — then top up with
    # the most-read stories from anywhere else so the row is always full
    # even in a category that only holds one or two pieces.
    related = list(Article.objects.published().with_relations()
                   .filter(category=article.category)
                   .exclude(pk=article.pk)[:RELATED_COUNT])
    if len(related) < RELATED_COUNT:
        seen = [article.pk] + [a.pk for a in related]
        related += list(Article.objects.published().with_relations()
                        .exclude(pk__in=seen)
                        .order_by("-view_count", "-publish_at")
                        [:RELATED_COUNT - len(related)])

    context = {
        "article": article,
        "comments": comments,
        "comment_count": article.comments.filter(is_approved=True).count(),
        "form": form,
        "related": related,
    }
    return render(request, "news/article_detail.html", context)


@require_POST
def post_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        # Auto-approve in the demo; flip to False to require moderation.
        comment.is_approved = True
        comment.save()
        messages.success(request, _("Your comment has been posted."))
    else:
        messages.error(request, _("Please correct the errors in your comment."))
    return redirect(article.get_absolute_url() + "#discussion")


def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = list(Article.objects.published().with_relations()
                    .filter(category=category))
    lead, rest = (articles[0], articles[1:]) if articles else (None, [])
    return render(request, "news/category.html",
                  {"category": category, "lead": lead, "articles": rest})


def tag_page(request, slug):
    from .models import Tag
    tag = get_object_or_404(Tag, slug=slug)
    articles = list(Article.objects.published().with_relations().filter(tags=tag))
    lead, rest = (articles[0], articles[1:]) if articles else (None, [])
    return render(request, "news/category.html",
                  {"category": tag, "lead": lead, "articles": rest, "is_tag": True})


def _search_qs(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("category", "").strip()
    order = request.GET.get("sort", "relevance")
    qs = Article.objects.published().with_relations()
    if q:
        # Search every language column, not just the default one — a reader
        # browsing in Urdu types Urdu, and an article may only carry its
        # Urdu translation in `title_ur`.
        text_fields = []
        for base in ("title", "excerpt", "body", "tags__name"):
            text_fields.append(base)
            text_fields += [f"{base}_{code}" for code in ("en", "ur", "ar")]
        matches = Q()
        for field in text_fields:
            matches |= Q(**{f"{field}__icontains": q})
        qs = qs.filter(matches).distinct()
    if cat:
        qs = qs.filter(category__slug=cat)
    if order == "recent":
        qs = qs.order_by("-publish_at")
    elif order == "popular":
        qs = qs.order_by("-view_count")
    return qs, q, cat, order


def search(request):
    qs, q, cat, order = _search_qs(request)
    return render(request, "news/search.html", {
        "results": qs[:40], "q": q, "active_category": cat, "sort": order,
        "categories": Category.objects.all(),
    })


def search_api(request):
    """JSON endpoint powering the live search dropdown (vanilla fetch)."""
    qs, q, _cat, _order = _search_qs(request)
    data = [{
        "title": a.title,
        "url": a.get_absolute_url(),
        "category": a.category.name,
        "kicker": a.kicker,
    } for a in qs[:8]]
    return JsonResponse({"query": q, "count": len(data), "results": data})


def markets_api(request):
    """JSON endpoint for the currency converter widget."""
    from .models import MarketRate
    rates = {r.pair.replace(" ", ""): float(r.rate) for r in MarketRate.objects.all()}
    return JsonResponse({"rates": rates})


def live_tv(request):
    streams = WidgetData.objects.filter(kind=WidgetData.Kind.LIVE_TV, is_active=True)
    return render(request, "news/live_tv.html", {"streams": streams})


def widgets_page(request):
    context = {
        "transport": WidgetData.objects.filter(kind=WidgetData.Kind.TRANSPORT, is_active=True),
        "horoscope": WidgetData.objects.filter(kind=WidgetData.Kind.HOROSCOPE, is_active=True),
        "islamic": WidgetData.objects.filter(kind=WidgetData.Kind.ISLAMIC, is_active=True),
    }
    return render(request, "news/widgets.html", context)


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            try:
                send_mail(
                    subject=f"[{inquiry.get_department_display()}] {inquiry.subject}",
                    message=f"From {inquiry.name} <{inquiry.email}>\n\n{inquiry.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=settings.CONTACT_RECIPIENTS,
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, _("Thank you — your message has been sent."))
            return redirect("news:contact")
    else:
        form = ContactForm()
    return render(request, "news/contact.html", {"form": form})


def signup(request):
    """Reader registration. Logs the new account straight in on success,
    matching the "stay signed in" session behaviour the rest of the
    site already gets for free from Django's session middleware."""
    if request.user.is_authenticated:
        return redirect("news:blog_list")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, _("Welcome to Al-Jarida — your account is ready."))
            return redirect("news:blog_list")
    else:
        form = SignUpForm()
    return render(request, "news/signup.html", {"form": form})


@ensure_csrf_cookie
def blog_list(request):
    """Public feed of every reader-written blog post, newest first.

    The page itself is server-rendered (so there's no flash of the wrong
    Write/Sign-in state on first paint), but the feed, the composer, and
    all CRUD actions are then driven client-side by static/js/blog.js
    against the JSON endpoints below — see api_blog_posts /
    api_blog_post_detail. ``ensure_csrf_cookie`` guarantees the csrftoken
    cookie is present for that JS to read before it ever needs to POST.
    """
    posts = BlogPost.objects.select_related("author").all()
    return render(request, "news/blog_list.html", {"posts": posts})


@login_required(login_url="news:login")
def blog_create(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, _("Post published."))
            return redirect("news:blog_list")
    else:
        form = BlogPostForm()
    return render(request, "news/blog_form.html", {"form": form, "editing": False})


@login_required(login_url="news:login")
def blog_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    # Ownership is enforced server-side regardless of what the UI shows —
    # the Edit/Delete buttons are hidden from non-owners in the template,
    # but that alone is not a security boundary.
    if post.author_id != request.user.id:
        messages.error(request, _("You can only edit your own posts."))
        return redirect("news:blog_list")

    if request.method == "POST":
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, _("Post updated."))
            return redirect("news:blog_list")
    else:
        form = BlogPostForm(instance=post)
    return render(request, "news/blog_form.html",
                  {"form": form, "editing": True, "post": post})


@login_required(login_url="news:login")
@require_POST
def blog_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if post.author_id != request.user.id:
        messages.error(request, _("You can only delete your own posts."))
    else:
        post.delete()
        messages.success(request, _("Post deleted."))
    return redirect("news:blog_list")


# ============================================================
# Reader blog — JSON API for the JS-driven module (static/js/blog.js)
#
# Auth here still runs entirely on Django's real session (password
# hashing, CSRF, the same SignUpForm/AuthenticationForm the server-
# rendered pages use) — these views just return JSON instead of a
# redirect/rendered page. The frontend caches the returned user in
# LocalStorage purely as a UI convenience (instant show/hide of the
# Write section, no flash while /api/auth/me/ round-trips); the
# session cookie remains the actual security boundary, and every
# mutating endpoint re-checks request.user / ownership server-side
# regardless of what the client claims.
# ============================================================

def _user_json(user):
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.get_full_name() or user.username,
        "email": user.email,
    }


def _post_json(post, request):
    return {
        "id": post.pk,
        "title": post.title,
        "content": post.content,
        "title_dir": post.title_dir,
        "content_dir": post.content_dir,
        "author_id": post.author_id,
        "author_name": post.author_name,
        "created_at": post.created_at.isoformat(),
        "created_at_display": date_format(timezone.localtime(post.created_at), "F j, Y"),
        "is_owner": request.user.is_authenticated and post.author_id == request.user.id,
    }


def _json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except (TypeError, ValueError):
        return {}


@require_http_methods(["GET"])
def api_me(request):
    """Who's actually signed in, per the real session — the ground truth
    the frontend reconciles its LocalStorage cache against on load."""
    if request.user.is_authenticated:
        return JsonResponse({"user": _user_json(request.user)})
    return JsonResponse({"user": None})


@require_POST
def api_login(request):
    if request.user.is_authenticated:
        return JsonResponse({"user": _user_json(request.user)})
    form = AuthenticationForm(request, data=_json_body(request))
    if form.is_valid():
        auth_login(request, form.get_user())
        return JsonResponse({"user": _user_json(request.user)})
    return JsonResponse({"error": str(_("Incorrect username or password."))}, status=400)


@require_POST
def api_signup(request):
    if request.user.is_authenticated:
        return JsonResponse({"user": _user_json(request.user)})
    form = SignUpForm(_json_body(request))
    if form.is_valid():
        user = form.save()
        auth_login(request, user)
        return JsonResponse({"user": _user_json(user)}, status=201)
    return JsonResponse({"errors": form.errors}, status=400)


@require_POST
def api_logout(request):
    auth_logout(request)
    return JsonResponse({"ok": True})


def api_blog_posts(request):
    if request.method == "GET":
        posts = BlogPost.objects.select_related("author").all()
        return JsonResponse({"posts": [_post_json(p, request) for p in posts]})

    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": str(_("Sign in required."))}, status=401)
        form = BlogPostForm(_json_body(request))
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return JsonResponse({"post": _post_json(post, request)}, status=201)
        return JsonResponse({"errors": form.errors}, status=400)

    return HttpResponseNotAllowed(["GET", "POST"])


def api_blog_post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if request.method in ("PUT", "PATCH"):
        if not request.user.is_authenticated:
            return JsonResponse({"error": str(_("Sign in required."))}, status=401)
        if post.author_id != request.user.id:
            return JsonResponse({"error": str(_("You can only edit your own posts."))}, status=403)
        form = BlogPostForm(_json_body(request), instance=post)
        if form.is_valid():
            form.save()
            return JsonResponse({"post": _post_json(post, request)})
        return JsonResponse({"errors": form.errors}, status=400)

    if request.method == "DELETE":
        if not request.user.is_authenticated:
            return JsonResponse({"error": str(_("Sign in required."))}, status=401)
        if post.author_id != request.user.id:
            return JsonResponse({"error": str(_("You can only delete your own posts."))}, status=403)
        post.delete()
        return JsonResponse({"ok": True})

    return HttpResponseNotAllowed(["PUT", "PATCH", "DELETE"])


def directory(request):
    return render(request, "news/directory.html")


def legal(request, page):
    titles = {
        "privacy": _("Privacy Policy"),
        "terms": _("Terms of Use"),
        "copyright": _("Copyright & IP Compliance"),
    }
    if page not in titles:
        from django.http import Http404
        raise Http404()
    return render(request, "news/legal.html",
                  {"page": page, "page_title": titles[page]})

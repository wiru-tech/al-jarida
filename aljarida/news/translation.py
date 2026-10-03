"""Per-language database fields for editorial content.

`django-modeltranslation` reads this module at startup and, for every field
named below, adds one physical column per language in ``settings.LANGUAGES``
(``title_en`` / ``title_ur`` / ``title_ar`` …). It then replaces the original
attribute with a descriptor that returns the column matching the *active*
request language, falling back to English when a translation is blank.

The practical consequence is that no template or queryset has to change:
``{{ article.title }}`` keeps working and simply starts returning Urdu when
Urdu is the active language. Only fields holding editorial prose are
registered — slugs, dates, counters and image paths stay single-valued so
URLs and media remain stable across languages.
"""
from modeltranslation.translator import TranslationOptions, register

from .models import Article, Author, Category, Tag, WidgetData


@register(Author)
class AuthorTranslationOptions(TranslationOptions):
    # Byline job title (e.g. "Senior Political Correspondent") is editorial
    # prose shown next to the article, so it needs the same per-language
    # treatment as the article fields below.
    fields = ("role",)


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    # `name` is what the nav menu prints, so translating it is what makes the
    # admin-managed menu appear in Urdu/Arabic rather than only the fixed
    # `kind` labels (which come from gettext, not the database).
    fields = ("name", "description")


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ("title", "kicker", "excerpt", "body", "image_caption")


@register(WidgetData)
class WidgetDataTranslationOptions(TranslationOptions):
    # Sidebar/quote/live-TV copy is database-authored chrome, so it needs the
    # same treatment as articles or the sidebar stays English on RTL pages.
    fields = ("title", "subtitle", "body")

"""Customised Django admin — the newsroom control panel.

Models whose text is registered in news/translation.py inherit from
``TabbedTranslationAdmin``, which renders one tab per language (English /
Urdu / Arabic) above each translatable field, so an editor fills in all three
versions on a single form instead of maintaining parallel records.
"""
from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from .models import (Article, Author, BlogPost, Category, Comment,
                     ContactInquiry, GalleryImage, MarketRate, Tag,
                     WidgetData)


class GalleryInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("name", "body", "is_approved", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "kind", "order", "show_in_nav", "show_on_home", "swatch")
    list_editable = ("order", "show_in_nav", "show_on_home")
    # The slug is deliberately single-valued (URLs stay stable across
    # languages), so it is seeded from the English name only.
    prepopulated_fields = {"slug": ("name_en",)}
    search_fields = ("name", "name_en", "name_ur", "name_ar")

    @admin.display(description="Accent")
    def swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:16px;height:16px;'
            'border-radius:2px;background:{}"></span>', obj.accent_color)


@admin.register(Article)
class ArticleAdmin(TabbedTranslationAdmin):
    list_display = ("title", "category", "author", "status",
                    "is_featured", "is_breaking", "publish_at", "view_count")
    list_filter = ("status", "category", "language", "is_featured", "is_breaking")
    list_editable = ("status", "is_featured", "is_breaking")
    search_fields = ("title", "title_ur", "title_ar",
                     "excerpt", "excerpt_ur", "excerpt_ar", "body")
    prepopulated_fields = {"slug": ("title_en",)}
    autocomplete_fields = ("category", "author", "tags")
    date_hierarchy = "publish_at"
    inlines = [GalleryInline, CommentInline]
    readonly_fields = ("view_count",)
    fieldsets = (
        ("Headline", {"fields": ("title", "slug", "kicker", "excerpt")}),
        ("Body", {"fields": ("body", "body_secondary", "secondary_language")}),
        ("Taxonomy", {"fields": ("category", "tags", "author", "language")}),
        ("Media", {"fields": ("featured_image", "featured_image_url",
                              "image_caption", "video_embed_url", "video_file")}),
        ("Publishing", {"fields": ("status", "is_featured", "is_breaking",
                                   "publish_at", "read_minutes", "view_count")}),
    )
    actions = ["make_published"]

    @admin.action(description="Publish selected articles now")
    def make_published(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status=Article.Status.PUBLISHED,
                                  publish_at=timezone.now())
        self.message_user(request, f"{updated} article(s) published.")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "article", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    list_editable = ("is_approved",)
    search_fields = ("name", "body")
    actions = ["approve"]

    @admin.action(description="Approve selected comments")
    def approve(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("display_name", "role")
    search_fields = ("display_name", "role")


@admin.register(Tag)
class TagAdmin(TabbedTranslationAdmin):
    list_display = ("name",)
    search_fields = ("name", "name_ur", "name_ar")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(MarketRate)
class MarketRateAdmin(admin.ModelAdmin):
    list_display = ("pair", "rate", "change_pct", "order")
    list_editable = ("rate", "change_pct", "order")


@admin.register(WidgetData)
class WidgetDataAdmin(TabbedTranslationAdmin):
    list_display = ("title", "kind", "is_active", "order")
    list_filter = ("kind", "is_active")
    list_editable = ("is_active", "order")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "content_dir", "created_at")
    list_filter = ("content_dir", "created_at")
    search_fields = ("title", "content", "author__username", "author__email")
    readonly_fields = ("title_dir", "content_dir", "created_at", "updated_at")


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("subject", "department", "name", "is_handled", "created_at")
    list_filter = ("department", "is_handled")
    list_editable = ("is_handled",)
    search_fields = ("subject", "name", "email", "message")
    readonly_fields = ("created_at", "updated_at")

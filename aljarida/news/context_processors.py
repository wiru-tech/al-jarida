"""Site-wide template context: nav categories, breaking ticker, widgets, markets."""
from .models import Article, Category, MarketRate, WidgetData
from .templatetags.i18n_extras import content_lang


def site_globals(request):
    nav_categories = Category.objects.filter(show_in_nav=True)

    # `.values_list()` reads raw columns and so bypasses the per-language
    # descriptors modeltranslation installs — it would always emit English.
    # Iterate real instances so `.title` resolves to the active language,
    # and record which language each headline actually landed in so the
    # template can mark fallbacks for rtl.css (see content_lang filter).
    breaking = [
        {"title": a.title, "slug": a.slug, "lang": content_lang(a)}
        for a in Article.objects.published().filter(is_breaking=True)[:8]
    ]

    most_read = (Article.objects.published()
                 .with_relations()
                 .order_by("-view_count")[:4])

    markets = MarketRate.objects.all()[:5]

    live_tv = WidgetData.objects.filter(kind=WidgetData.Kind.LIVE_TV,
                                        is_active=True).first()
    quote = WidgetData.objects.filter(kind=WidgetData.Kind.QUOTE,
                                      is_active=True).first()

    return {
        "nav_categories": nav_categories,
        "breaking_items": breaking,
        "sidebar_most_read": most_read,
        "sidebar_markets": markets,
        "sidebar_live_tv": live_tv,
        "sidebar_quote": quote,
        "LANGUAGES_RTL": ("ur", "ar"),
    }

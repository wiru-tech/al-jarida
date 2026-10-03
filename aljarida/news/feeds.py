"""RSS feed for news syndication."""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import strip_tags

from .models import Article


class LatestArticlesFeed(Feed):
    feed_type = Rss201rev2Feed
    title = "AL-JARIDA — Latest Dispatch"
    link = "/"
    description = "The latest news and editorial coverage from Al-Jarida."

    def items(self):
        return Article.objects.published().with_relations()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or strip_tags(item.body)[:200]

    def item_link(self, item):
        return reverse("news:article", args=[item.slug])

    def item_pubdate(self, item):
        return item.publish_at

    def item_categories(self, item):
        return [item.category.name]

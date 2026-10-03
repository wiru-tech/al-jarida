from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .feeds import LatestArticlesFeed

app_name = "news"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("api/search/", views.search_api, name="search_api"),
    path("api/markets/", views.markets_api, name="markets_api"),
    path("contact/", views.contact, name="contact"),
    path("directory/", views.directory, name="directory"),
    path("live-tv/", views.live_tv, name="live_tv"),
    path("widgets/", views.widgets_page, name="widgets"),
    path("legal/<slug:page>/", views.legal, name="legal"),
    path("rss/", LatestArticlesFeed(), name="rss"),

    # Reader accounts (Sign Up / Sign In / Sign Out)
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/login/", auth_views.LoginView.as_view(
        template_name="news/login.html", redirect_authenticated_user=True,
    ), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(
        next_page="news:home",
    ), name="logout"),

    # Reader blog (sign-in-only create/edit/delete; list is public)
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/new/", views.blog_create, name="blog_create"),
    path("blog/<int:pk>/edit/", views.blog_edit, name="blog_edit"),
    path("blog/<int:pk>/delete/", views.blog_delete, name="blog_delete"),

    # Reader blog — JSON API for the JS-driven module (static/js/blog.js)
    path("api/auth/me/", views.api_me, name="api_me"),
    path("api/auth/login/", views.api_login, name="api_login"),
    path("api/auth/signup/", views.api_signup, name="api_signup"),
    path("api/auth/logout/", views.api_logout, name="api_logout"),
    path("api/blog/posts/", views.api_blog_posts, name="api_blog_posts"),
    path("api/blog/posts/<int:pk>/", views.api_blog_post_detail, name="api_blog_post_detail"),

    path("tag/<slug:slug>/", views.tag_page, name="tag"),
    path("category/<slug:slug>/", views.category_page, name="category"),
    path("<slug:slug>/comment/", views.post_comment, name="post_comment"),
    path("<slug:slug>/", views.article_detail, name="article"),
]

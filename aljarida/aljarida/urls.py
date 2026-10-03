from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import set_language

admin.site.site_header = "AL-JARIDA Newsroom"
admin.site.site_title = "AL-JARIDA Admin"
admin.site.index_title = "Editorial Control Panel"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("i18n/setlang/", set_language, name="set_language"),
    path("", include("news.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("pages.urls")),
    path('reader/', include('reader.urls')),
    path('', include('reader.urls')),  # The URLs from the 'reader' app will be included without the 'reader/' prefix
    path("__reload__/", include("django_browser_reload.urls")),


]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

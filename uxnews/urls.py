from django.conf import settings
from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
from django.conf.urls.static import static
=======
>>>>>>> 01e5779932cb5b80a3b140e4d4d7a2e2d1408720

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("pages.urls")),
    path('reader/', include('reader.urls')),
    path('', include('reader.urls')),  # The URLs from the 'reader' app will be included without the 'reader/' prefix
    path("__reload__/", include("django_browser_reload.urls")),

<<<<<<< HEAD
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======

]
>>>>>>> 01e5779932cb5b80a3b140e4d4d7a2e2d1408720

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

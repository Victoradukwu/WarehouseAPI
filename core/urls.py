from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui", ),
    path("", include("warehouse.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

if settings.ENVIRONMENT not in ("production", "staging", "lab"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

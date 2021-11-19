from django.urls import path

from .conf import settings


urlpatterns = [
    path(
        settings.HEALTH_CHECK_PATTERN,
        HealthCheckView.as_view()
    )
]

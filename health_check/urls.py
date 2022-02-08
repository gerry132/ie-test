# -*- coding: utf-8 -*-
from django.urls import path

from .conf import settings
from .views import HealthCheckView


urlpatterns = [
    path(
        settings.HEALTH_CHECK_PATTERN,
        HealthCheckView.as_view()
    )
]

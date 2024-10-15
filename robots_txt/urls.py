# -*- coding: utf-8 -*-
from django.urls import path

from .conf import settings
from django.views.generic import TemplateView


urlpatterns = [
    path(
        settings.ROBOTS_PATTERN,
        TemplateView.as_view(template_name="base.html")
    )
]

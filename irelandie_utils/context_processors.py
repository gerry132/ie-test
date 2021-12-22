# -*- coding: utf-8 -*-
from django.conf import settings

from irelandie_utils.models import Tracking


def global_vars(request):
    tracking = Tracking.for_request(request)
    return {
        "GOOGLE_TAG_MANAGER_ID": getattr(tracking, "google_tag_manager_id", None),
        "SEO_NOINDEX": settings.SEO_NOINDEX,
    }

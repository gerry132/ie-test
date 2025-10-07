from django.utils.deprecation import MiddlewareMixin
from wagtail.admin.auth import require_admin_access

from irelandie_admin import views as override_views


class ReplaceViewsMiddleware(MiddlewareMixin):
    replacements = {
        "wagtailadmin_pages:search": override_views.search,
    }

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

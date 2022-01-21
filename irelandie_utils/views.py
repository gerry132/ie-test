# -*- coding: utf-8 -*-
from django.views import defaults
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import PagesAPIViewSet

from irelandie_missions.filters import MissionPageFieldFilter
from irelandie_utils.utils import get_locale_from_language_code_or_default


def page_not_found(request, exception, template_name="patterns/pages/errors/404.html"):
    return defaults.page_not_found(request, exception, template_name)


def server_error(request, template_name="patterns/pages/errors/500.html"):
    return defaults.server_error(request, template_name)


class PagesAPIEndpoint(PagesAPIViewSet):
    base_serializer_class = PageSerializer
    filter_backends = [
        # NOTE: filters should be listed before the SearchFilter
      MissionPageFieldFilter,
    ] + PagesAPIViewSet.filter_backends
    known_query_parameters = PagesAPIViewSet.known_query_parameters.union([
        "mission",
        "country",
        "country_group"
    ])

    def get_serializer_context(self):
        context = super().get_serializer_context()

        # If this request access a page, put the page locale in the context
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in self.kwargs:
            context.update({"locale": self.get_object().locale})
        # Get the locale from GET parameter
        elif (request := self.request) and "locale" in request.GET:
            locale = get_locale_from_language_code_or_default(request.GET.get("locale"))
            context.update({"locale": locale})

        return context

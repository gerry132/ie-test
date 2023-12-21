# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import check_for_language
from django.views import defaults
from django.views.decorators.http import require_http_methods
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.models import Page

from irelandie_missions.filters import MissionPageFieldFilter
from irelandie_utils.utils import get_locale_from_language_code_or_default


def page_not_found(request, exception, template_name="patterns/pages/errors/404.html"):
    if '/%s/' % (request.LANGUAGE_CODE) in request.get_raw_uri() and request.LANGUAGE_CODE != 'en':
        return redirect(request.get_raw_uri().replace('/%s/' % (request.LANGUAGE_CODE), '/en/'))
    return defaults.page_not_found(request, exception, template_name)


def server_error(request, template_name="patterns/pages/errors/500.html"):
    return defaults.server_error(request, template_name)


class PagesAPIEndpoint(PagesAPIViewSet):
    base_serializer_class = PageSerializer
    filter_backends = [
        # NOTE: filters should be listed before the SearchFilter
        MissionPageFieldFilter,
    ] + PagesAPIViewSet.filter_backends
    known_query_parameters = PagesAPIViewSet.known_query_parameters.union(
        ["mission", "country", "country_group"]
    )

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


@require_http_methods(["POST"])
def set_language_wagtail(request):
    page_id = request.POST.get("page_id")
    lang_code = request.POST.get("language")
    next_url = "/"
    if page_id and lang_code and check_for_language(lang_code):
        try:
            next_url = (
                Page.objects.get(pk=page_id)
                .get_translations()
                .get(locale__language_code=lang_code)
                .url
            )
        except (Page.DoesNotExist, Page.MultipleObjectsReturned):
            pass
    response = HttpResponseRedirect(next_url)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang_code,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response

# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.translation import check_for_language
from django.views import defaults
from django.views.decorators.http import require_http_methods
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.models import Page

from irelandie_missions.filters import MissionPageFieldFilter
from irelandie_news.models import NewsPage
from irelandie_utils.models import SystemMessagesSettings
from wagtail.core.models import Site
from irelandie_utils.utils import get_locale_from_language_code_or_default


def page_not_found(request, exception, template_name="patterns/pages/errors/404.html"):
    if '/%s/' % (request.LANGUAGE_CODE) in request.get_raw_uri() and request.LANGUAGE_CODE != 'en':
        return redirect(request.get_raw_uri().replace('/%s/' % (request.LANGUAGE_CODE), '/en/'))
    return defaults.page_not_found(request, exception, template_name)


def server_error(request, template_name="patterns/pages/errors/500.html"):
    try:
        current_site = Site.find_for_request(request)
        system_messages_settings = SystemMessagesSettings.for_site(current_site)
        title_403_500 = system_messages_settings.title_403_500
        body_403_500 = system_messages_settings.body_403_500
        image_403_500 = system_messages_settings.image_403_500
    except (SystemMessagesSettings.DoesNotExist, Site.DoesNotExist):
        title_403_500 = "Something went wrong on our side"
        body_403_500 = ("<p>Sorry, this page is not working properly. "
                        "We now know about this and we’re working to fix it.</p>")
        image_403_500 = None

    return render(request, template_name,
                  {'title': title_403_500, 'body': body_403_500, 'image_error': image_403_500},
                  status=500)


def permission_denied(request, template_name="patterns/pages/errors/403.html"):
    try:
        current_site = Site.find_for_request(request)
        system_messages_settings = SystemMessagesSettings.for_site(current_site)
        title_403_500 = system_messages_settings.title_403_500
        body_403_500 = system_messages_settings.body_403_500
        image_403_500 = system_messages_settings.image_403_500
    except (SystemMessagesSettings.DoesNotExist, Site.DoesNotExist):
        title_403_500 = "Something went wrong on our side"
        body_403_500 = ("<p>Sorry, this page is not working properly. "
                        "We now know about this and we’re working to fix it.</p>")
        image_403_500 = None

    return render(request, template_name,
                  {'title': title_403_500, 'body': body_403_500, 'image_error': image_403_500},
                  status=403)


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


class NewsPageAPIEndpoint(PagesAPIViewSet):
    model = NewsPage

    """def test():
        year = None
        if request.GET.get('year'):
            if request.GET.get('year') == 'all':
                year = None
            else:
                year = int(request.GET.get('year'))
                low_date = datetime.datetime(year, 1, 1)
                high_date = datetime.datetime(year, 12, 31)

        elif 'year' in request.GET:
            if request.GET['year']:
                year = int(request.GET['year'])
                low_date = datetime.datetime(year, 1, 1)
                high_date = datetime.datetime(year, 12, 31)
            else:
                year = None
        else:
            high_date = datetime.datetime.now()
            low_date = datetime.datetime(high_date.year, 1, 1)
        if year:
            rel_art = (
                NewsPage.objects.child_of(self)
                .filter(publication_date__lte=high_date,
                        publication_date__gte=low_date,
                        locale=self.locale)
                .exclude(pk=self.pk)
                .public()
                .live()
                .order_by("-publication_date")
                .specific()
            )
        else:
            rel_art = (
                NewsPage.objects.child_of(self)
                .exclude(pk=self.pk)
                .public()
                .live()
                .order_by("-publication_date")
                .specific()
            )
        paginator = Paginator(rel_art, 20)
        # Try to get the ?page=x value
        page = request.GET.get("page", 1)
        try:
            rel_art = paginator.page(page)
        except PageNotAnInteger:
            rel_art = paginator.page(1)
        except EmptyPage:
            rel_art = paginator.page(paginator.num_pages)
        context['related_articles'] = rel_art
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = get_model_info(p.content_type.name, p.id)
                if missions.root_page:
                    context['mission_web_bot'] = missions.web_bot_script
        return context
"""


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

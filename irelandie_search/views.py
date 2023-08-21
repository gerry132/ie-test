# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.utils.cache import add_never_cache_headers, patch_cache_control

from irelandie_missions.models import MissionPage

from wagtail.models import Page, Site
from irelandie_tags.models import TagPage, DestinationTagPage
from irelandie_utils.cache import get_default_cache_control_kwargs

from wagtail.search.backends import get_search_backend
from wagtail.search.query import Fuzzy


def search(request):
    root_page = Site.find_for_request(request).root_page.localized
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)
    origin = request.GET.get("query_type")
    # Search

    if origin:
        root_page = MissionPage.objects.live().get(id=origin)

    if search_query:
        s = get_search_backend()

        if hasattr(s, 'settings'):
            search_results = (
                Page.objects.live().public()
                    .descendant_of(root_page)
                    .not_exact_type(TagPage, DestinationTagPage)
                    .search(Fuzzy(search_query), partial_match=False)
            )
        else:
            search_results = (
                Page.objects.live().public()
                    .descendant_of(root_page)
                    .not_exact_type(TagPage, DestinationTagPage)
                    .search(search_query, operator="and", partial_match=True)
            )
    else:
        search_results = Page.objects.none()
    # Pagination
    paginator = Paginator(search_results, settings.DEFAULT_PER_PAGE)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    response = TemplateResponse(
        request,
        "patterns/pages/search/search.html",
        {"search_query": search_query, "search_results": search_results, "page": page},
    )
    # Instruct FE cache to not cache when the search query is present.
    # It's so hits get added to the database and results include newly
    # added pages.
    if search_query:
        add_never_cache_headers(response)
    else:
        patch_cache_control(response, **get_default_cache_control_kwargs())
    return response

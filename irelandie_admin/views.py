from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import Http404
from django.http.request import QueryDict
from django.template.response import TemplateResponse
from django.views.decorators.vary import vary_on_headers
from irelandie_missions.models import DestinationPage
from wagtail.admin.auth import user_has_any_page_permission, user_passes_test
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.views.pages.search import page_filter_search
from wagtail.core.models import Page
from wagtail.search.query import MATCH_ALL


@vary_on_headers("X-Requested-With")
@user_passes_test(user_has_any_page_permission)
def search(request):
    pages = all_pages = Page.objects.all().prefetch_related("content_type").specific()
    q = MATCH_ALL
    content_types = []
    pagination_query_params = QueryDict({}, mutable=True)
    ordering = None
    country_pages = DestinationPage.objects.all().order_by('locale__id', 'title')

    if "ordering" in request.GET:
        if request.GET["ordering"] in [
            "title",
            "-title",
            "latest_revision_created_at",
            "-latest_revision_created_at",
            "live",
            "-live",
        ]:
            ordering = request.GET["ordering"]

            if ordering == "title":
                pages = pages.order_by("title")
            elif ordering == "-title":
                pages = pages.order_by("-title")

            if ordering == "latest_revision_created_at":
                pages = pages.order_by("latest_revision_created_at")
            elif ordering == "-latest_revision_created_at":
                pages = pages.order_by("-latest_revision_created_at")

            if ordering == "live":
                pages = pages.order_by("live")
            elif ordering == "-live":
                pages = pages.order_by("-live")

    if "content_type" in request.GET:
        pagination_query_params["content_type"] = request.GET["content_type"]

        try:
            app_label, model_name = request.GET["content_type"].split(".")
        except ValueError:
            raise Http404

        try:
            selected_content_type = ContentType.objects.get_by_natural_key(
                app_label, model_name
            )
        except ContentType.DoesNotExist:
            raise Http404

        pages = pages.filter(content_type=selected_content_type)
    else:
        selected_content_type = None

    selected_country = None
    if "parent_country" in request.GET and request.GET["parent_country"]:
        selected_country = int(request.GET["parent_country"])
        country_obj = DestinationPage.objects.get(pk=selected_country)
        pages = pages.descendant_of(country_obj)
        all_pages = all_pages.descendant_of(country_obj)

    if "q" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            q = form.cleaned_data["q"]
            pagination_query_params["q"] = q

            # Parse query and filter
            pages, all_pages = page_filter_search(q, pages, all_pages, ordering)

            # Facets
            if pages.supports_facet:
                content_types = [
                    (ContentType.objects.get(id=content_type_id), count)
                    for content_type_id, count in all_pages.facet(
                        "content_type_id"
                    ).items()
                ]

    else:
        form = SearchForm()

    paginator = Paginator(pages, per_page=20)
    pages = paginator.get_page(request.GET.get("p"))

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return TemplateResponse(
            request,
            "wagtailadmin/pages/search_results.html",
            {
                "pages": pages,
                "all_pages": all_pages,
                "query_string": q if q != MATCH_ALL else "",
                "content_types": content_types,
                "selected_content_type": selected_content_type,
                "ordering": ordering,
                "pagination_query_params": pagination_query_params.urlencode(),
                "country_pages": country_pages,
                "selected_country": selected_country,
            },
        )
    else:
        return TemplateResponse(
            request,
            "wagtailadmin/pages/search.html",
            {
                "search_form": form,
                "pages": pages,
                "all_pages": all_pages,
                "query_string": q if q != MATCH_ALL else "",
                "content_types": content_types,
                "selected_content_type": selected_content_type,
                "ordering": ordering,
                "pagination_query_params": pagination_query_params.urlencode(),
                "country_pages": country_pages,
                "selected_country": selected_country,
            },
        )

from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpRequest

from irelandie_news.models import NewsPage
from irelandie_api.views.utils import get_queryset # noqa


def api_pagination_partial(request: HttpRequest):
    page_number = int(request.GET.get("page", 1))
    year = request.GET.get("year")
    locale_code = request.GET.get("locale")
    parent_id = request.GET.get("child_of")

    qs = get_queryset(year, locale_code, parent_id, NewsPage)

    paginator = Paginator(qs, 10)
    paginator_page = paginator.get_page(page_number)

    context = {
        "paginator_page": paginator_page,
        "num_pages": paginator.num_pages,
        "page": page_number,
        "year": year,
    }

    return render(request, "patterns/molecules/pagination/api-pagination.html", context)

from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpRequest

from irelandie_news.models import NewsPage


def api_pagination_partial(request: HttpRequest):
    page_number = int(request.GET.get("page", 1))
    year = request.GET.get("year")

    queryset = NewsPage.objects.live().public()
    if year:
        queryset = queryset.filter(publication_date__year=year)

    paginator = Paginator(queryset, 10)
    paginator_page = paginator.get_page(page_number)

    context = {
        "paginator_page": paginator_page,
        "num_pages": paginator.num_pages,
        "page": page_number,
        "year": year,
    }

    return render(request, "patterns/molecules/pagination/api-pagination.html", context)


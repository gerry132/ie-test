from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from irelandie_news.models import NewsPage
from irelandie_api.serializers.news import NewsPageSerializer


class NewsPagePagination(LimitOffsetPagination):
    default_limit = 10


class NewsPageAPIView(ListAPIView):
    serializer_class = NewsPageSerializer
    pagination_class = NewsPagePagination

    def get_queryset(self):
        year = self.request.query_params.get("year")
        qs = NewsPage.objects.live().public().order_by("-publication_date")
        if year:
            qs = qs.filter(publication_date__year=year)
        return qs

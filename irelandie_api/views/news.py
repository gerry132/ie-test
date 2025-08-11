from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from irelandie_news.models import NewsPage
from irelandie_api.serializers.news import NewsPageSerializer
from irelandie_api.views.utils import get_queryset


class NewsPagePagination(LimitOffsetPagination):
    default_limit = 10


class NewsPageAPIView(ListAPIView):
    serializer_class = NewsPageSerializer
    pagination_class = NewsPagePagination

    def get_queryset(self):
        params = self.request.query_params
        year = params.get("year")
        locale_code = params.get("locale")
        parent_id = params.get("child_of")

        qs = get_queryset(year, locale_code, parent_id, NewsPage)
        return qs

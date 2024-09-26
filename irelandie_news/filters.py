from rest_framework.filters import BaseFilterBackend

import datetime

x = datetime.datetime(2020, 5, 17)


class NewsPageFieldFilter(BaseFilterBackend):
    indirect_query_parameters = {"title": "news"}
    year = "year"
    print(1234568678556876)
    def filter_queryset(self, request, queryset, view):
        print(12345)
        if "type" in request.GET and request.GET["type"] == "irelandie_news.NewsPage":
            for field_name in self.indirect_query_parameters:
                if field_name in request.GET:
                    value = request.GET[field_name]
                    queryset = queryset.filter(**{field_name: value})

            if self.year in request.GET:
                year = request.GET[self.year]
                date_range = self.get_date_range(int(year))
                queryset = queryset.filter(publication_date__gte=date_range['low'])
                queryset = queryset.filter(publication_date__lte=date_range['high'])

        return queryset

    @staticmethod
    def get_date_range(year):

        low = datetime.datetime(year, 1, 1)
        high = datetime.datetime(year, 12, 31)

        return {'high': high, 'low': low}

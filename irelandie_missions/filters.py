from rest_framework.filters import BaseFilterBackend

from irelandie_missions.models import CountryPage, CountryGroupPageIndex


class MissionPageFieldFilter(BaseFilterBackend):
    indirect_query_parameters = {"title": "mission"}
    country_parameter = "country"
    country_group_parameter = "country_group"

    def filter_queryset(self, request, queryset, view):

        if "type" in request.GET and request.GET["type"] == "irelandie_missions.MissionPage":
            for field_name in self.indirect_query_parameters:
                if field_name in request.GET:
                    value = request.GET[field_name]
                    queryset = queryset.filter(**{field_name: value})

            if self.country_parameter in request.GET:
                country = request.GET[self.country_parameter]
                country_page = CountryPage.objects.filter(title__iexact=country).first()
                queryset = queryset.child_of(country_page)

            if self.country_group_parameter in request.GET:
                country_group = request.GET[self.country_group_parameter]
                country_group_page = CountryGroupPageIndex.objects.filter(title__iexact=country_group).first()
                queryset = queryset.descendant_of(country_group_page)

        return queryset

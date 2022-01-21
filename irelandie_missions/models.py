# -*- coding: utf-8 -*-
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel

from irelandie_home.models import HomePage
from irelandie_utils.models import BasePage


class CountryGroupPageIndex(BasePage):
    template = "irelandie_assets/pages/countries.html"

    description = models.TextField(blank=True)

    parent_page_types = [HomePage]
    subpage_types = ["CountryPage"]

    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
    ]


class CountryPage(BasePage):
    template = "irelandie_assets/pages/country.html"

    parent_page_types = ["CountryGroupPageIndex"]
    subpage_types = ["MissionPage"]


class MissionPage(BasePage):
    template = "irelandie_assets/pages/mission.html"

    parent_page_types = ["CountryPage"]
    subpage_types = [
        "irelandie_alerts.AlertPageIndex",
        "irelandie_contact_details.ContactDetailPageIndex",
        "irelandie_corporate_information.CorportateInformationPageIndex",
        "irelandie_news.NewsPageIndex",
        "irelandie_people.PersonPageIndex",
        "irelandie_people.RolePageIndex",
        "irelandie_places.PlacePageIndex",
        "irelandie_publications.PublicationPageIndex",
        "irelandie_site_information.SiteInformationPageIndex",
    ]

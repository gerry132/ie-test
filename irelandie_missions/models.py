# -*- coding: utf-8 -*-
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page, TranslatableMixin

from irelandie_home.models import HomePage


class CountryGroupPageIndex(Page, TranslatableMixin):

    description = models.TextField(blank=True)

    parent_page_types = [HomePage]
    subpage_types = ["CountryPage"]

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class CountryPage(Page, TranslatableMixin):

    parent_page_types = ["CountryGroupPageIndex"]
    subpage_types = ["MissionPage"]


class MissionPage(Page, TranslatableMixin):

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

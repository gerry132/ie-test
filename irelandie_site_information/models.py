# -*- coding: utf-8 -*-
from django import forms

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page, TranslatableMixin

from irelandie_missions.models import MissionPage
from irelandie_utils.models import BasePage, ArticlePage


class SiteInformationPageIndex(BasePage):

    parent_page_types = [MissionPage]
    subpage_types = ["SiteInformationPage"]
    max_count_per_parent = 1


class SiteInformationPage(ArticlePage):

    countries = ParentalManyToManyField("irelandie_missions.CountryPage", blank=True)

    parent_page_types = [
        "SiteInformationPageIndex",
    ]
    subpage_types = []

    content_panels = ArticlePage.content_panels + [
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

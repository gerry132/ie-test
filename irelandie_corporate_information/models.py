# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

from irelandie_missions.models import MissionPage
from irelandie_utils.models import ArticlePage, BasePage

from .blocks import CorporateInformationPageSectionBlock


class CorportateInformationPageIndex(BasePage):

    parent_page_types = [MissionPage]
    subpage_types = ["CorportateInformationPage"]
    max_count_per_parent = 1


class CorportateInformationPage(ArticlePage):

    countries = ParentalManyToManyField("irelandie_missions.CountryPage", blank=True)

    parent_page_types = ["CorportateInformationPageIndex"]
    subpage_types = []

    content_panels = ArticlePage.content_panels + [
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

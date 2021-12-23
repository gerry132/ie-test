# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

from irelandie_missions.models import MissionPage

from .blocks import SiteInformationPageSectionBlock


class SiteInformationPageIndex(Page, TranslatableMixin):

    parent_page_types = [MissionPage]
    subpage_types = ["SiteInformationPage"]
    max_count_per_parent = 1


class SiteInformationPage(Page, TranslatableMixin):

    description = models.TextField(blank=True)
    body = StreamField(
        [
            ("section", SiteInformationPageSectionBlock()),
        ],
        blank=True,
        null=True,
    )
    countries = ParentalManyToManyField("irelandie_missions.CountryPage", blank=True)

    parent_page_types = [
        "SiteInformationPageIndex",
    ]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        StreamFieldPanel("body"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

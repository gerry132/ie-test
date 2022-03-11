# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

# from irelandie_missions.models import MissionPage


class AlertPageIndex(Page, TranslatableMixin):

    # parent_page_types = [
    #     MissionPage,
    #     "irelandie_pages.FreeFormPage",
    # ]
    # subpage_types = ["AlertPage"]
    max_count_per_parent = 1


class AlertPage(Page, TranslatableMixin):

    DEFAULT_ALERT_TYPE_CHOICE = ("info", "Info")
    ALERT_TYPE_CHOICES = [
        DEFAULT_ALERT_TYPE_CHOICE,
        ("error", "Danger"),
        ("success", "Success"),
        ("warning", "Warning"),
    ]

    alert_type = models.CharField(
        max_length=255, choices=ALERT_TYPE_CHOICES, default=DEFAULT_ALERT_TYPE_CHOICE[0]
    )
    body = StreamField(
        [
            ("richtext", RichTextBlock()),
        ],
        blank=True,
        null=True,
    )
    countries = ParentalManyToManyField("irelandie_missions.CountryPage", blank=True)

    # parent_page_types = ["AlertPageIndex"]
    # subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("alert_type"),
        StreamFieldPanel("body"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

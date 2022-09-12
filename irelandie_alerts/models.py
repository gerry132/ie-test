# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, StreamFieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.fields import StreamField
from wagtail.models import Page, TranslatableMixin


class AlertPageIndex(Page, TranslatableMixin):
    max_count_per_parent = 1


class AlertPage(Page, TranslatableMixin):
    template = "patterns/molecules/streamfield/blocks/alert_block.html"

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
    countries = ParentalManyToManyField("irelandie_missions.DestinationPage", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("alert_type"),
        StreamFieldPanel("body"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

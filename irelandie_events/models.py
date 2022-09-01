# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

from .blocks import EventPageSectionBlock


class EventPageIndex(Page, TranslatableMixin):

    description = models.TextField(blank=True)
    max_count_per_parent = 1

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class EventPage(Page, TranslatableMixin):

    body = StreamField(
        [
            ("section", EventPageSectionBlock()),
        ],
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True)
    date = models.DateTimeField(blank=True, null=True)
    countries = ParentalManyToManyField("irelandie_missions.DestinationPage", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        StreamFieldPanel("body"),
        FieldPanel("date"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

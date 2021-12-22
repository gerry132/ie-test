# -*- coding: utf-8 -*-
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

from irelandie_missions.models import MissionPage

from .blocks import PlacePageSectionBlock


class PlacePageIndex(Page, TranslatableMixin):

    parent_page_types = [MissionPage]
    subpage_types = ["PlacePage"]
    max_count_per_parent = 1


class PlacePage(Page, TranslatableMixin):

    description = models.TextField(blank=True)
    body = StreamField(
        [
            ("section", PlacePageSectionBlock()),
        ],
        blank=True,
        null=True,
    )

    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    address_line_3 = models.CharField(max_length=255, blank=True)

    emails = models.CharField(max_length=255, blank=True)
    telephone_numbers = models.CharField(max_length=255, blank=True)
    faxes = models.CharField(max_length=255, blank=True)

    latitude = models.CharField(max_length=255, blank=True)
    longtitude = models.CharField(max_length=255, blank=True)

    opening_hours_monday_from = models.TimeField(blank=True, null=True)
    opening_hours_monday_to = models.TimeField(blank=True, null=True)
    opening_hours_tuesday_from = models.TimeField(blank=True, null=True)
    opening_hours_tuesday_to = models.TimeField(blank=True, null=True)
    opening_hours_wednesday_from = models.TimeField(blank=True, null=True)
    opening_hours_wednesday_to = models.TimeField(blank=True, null=True)
    opening_hours_thursday_from = models.TimeField(blank=True, null=True)
    opening_hours_thursday_to = models.TimeField(blank=True, null=True)
    opening_hours_friday_from = models.TimeField(blank=True, null=True)
    opening_hours_friday_to = models.TimeField(blank=True, null=True)
    opening_hours_saturday_from = models.TimeField(blank=True, null=True)
    opening_hours_saturday_to = models.TimeField(blank=True, null=True)
    opening_hours_sunday_from = models.TimeField(blank=True, null=True)
    opening_hours_sunday_to = models.TimeField(blank=True, null=True)

    parent_page_types = [
        "PlacePageIndex",
    ]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        StreamFieldPanel("body"),
        FieldPanel("latitude"),
        FieldPanel("longtitude"),
        FieldPanel("emails"),
        FieldPanel("telephone_numbers"),
        FieldPanel("faxes"),
        FieldPanel("opening_hours_monday_from"),
        FieldPanel("opening_hours_monday_to"),
        FieldPanel("opening_hours_tuesday_from"),
        FieldPanel("opening_hours_tuesday_to"),
        FieldPanel("opening_hours_wednesday_from"),
        FieldPanel("opening_hours_wednesday_to"),
        FieldPanel("opening_hours_thursday_from"),
        FieldPanel("opening_hours_thursday_to"),
        FieldPanel("opening_hours_friday_from"),
        FieldPanel("opening_hours_friday_to"),
        FieldPanel("opening_hours_saturday_from"),
        FieldPanel("opening_hours_saturday_to"),
        FieldPanel("opening_hours_sunday_from"),
        FieldPanel("opening_hours_sunday_to"),
    ]

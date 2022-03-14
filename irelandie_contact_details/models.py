# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

# from irelandie_missions.models import MissionPage


class ContactDetailPageIndex(Page, TranslatableMixin):

    # parent_page_types = [MissionPage]
    # subpage_types = ["ContactDetailPage"]
    max_count_per_parent = 1


class ContactDetailPage(Page, TranslatableMixin):

    description = models.TextField(blank=True)

    address_line_1 = models.CharField(blank=True, max_length=255)
    address_line_2 = models.CharField(blank=True, max_length=255)
    address_line_3 = models.CharField(blank=True, max_length=255)

    emails = models.CharField(blank=True, max_length=255)
    telephone_numbers = models.CharField(blank=True, max_length=255)
    faxes = models.CharField(blank=True, max_length=255)

    body = StreamField(
        [
            ("richtext", RichTextBlock()),
        ],
        blank=True,
        null=True,
    )
    countries = ParentalManyToManyField("irelandie_missions.CountryPage", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        StreamFieldPanel("body"),
        FieldPanel("description"),
        FieldPanel("emails"),
        FieldPanel("telephone_numbers"),
        FieldPanel("faxes"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

    # parent_page_types = [ContactDetailPageIndex]

# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, StreamFieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.fields import StreamField
from wagtail.models import Page, TranslatableMixin


class ContactDetailPageIndex(Page, TranslatableMixin):
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
    countries = ParentalManyToManyField("irelandie_missions.DestinationPage", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        StreamFieldPanel("body"),
        FieldPanel("description"),
        FieldPanel("emails"),
        FieldPanel("telephone_numbers"),
        FieldPanel("faxes"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

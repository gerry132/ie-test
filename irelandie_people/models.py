# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin
from wagtail.images.edit_handlers import ImageChooserPanel

from irelandie_missions.models import MissionPage

from .blocks import PersonPageSectionBlock, RolePageSectionBlock


class PersonPageIndex(Page, TranslatableMixin):

    parent_page_types = [MissionPage]
    subpage_types = ["PersonPage"]
    max_count_per_parent = 1


class PersonPage(Page, TranslatableMixin):

    description = models.TextField(blank=True)
    body = StreamField(
        [
            ("section", PersonPageSectionBlock()),
        ],
        blank=True,
        null=True,
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    countries = ParentalManyToManyField("irelandie_missions.CountryPage", blank=True)

    parent_page_types = [
        "PersonPageIndex",
    ]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        StreamFieldPanel("body"),
        ImageChooserPanel("image"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]


class RolePageIndex(Page, TranslatableMixin):

    parent_page_types = [MissionPage]
    subpage_types = ["RolePage"]
    max_count_per_parent = 1


class RolePage(Page, TranslatableMixin):

    PERSON_PAGE_MODEL = PersonPage

    description = models.TextField(blank=True)
    body = StreamField(
        [
            ("section", RolePageSectionBlock()),
        ],
        blank=True,
        null=True,
    )
    role_holder = models.ForeignKey(
        PERSON_PAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    countries = ParentalManyToManyField("irelandie_missions.CountryPage", blank=True)

    parent_page_types = [
        "RolePageIndex",
    ]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        StreamFieldPanel("body"),
        PageChooserPanel("role_holder"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

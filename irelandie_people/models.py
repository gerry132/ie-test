# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin
from wagtail.images.edit_handlers import ImageChooserPanel

from .blocks import PersonPageSectionBlock, RolePageSectionBlock


class PersonPageIndex(Page, TranslatableMixin):
    max_count_per_parent = 1


class PersonPage(Page, TranslatableMixin):
    # TODO: there is no person page template yet.
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
    image_alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Image Alt text"),
        help_text=_("The alt text shown for accessibility: https://axesslab.com/alt-texts/")
    )
    countries = ParentalManyToManyField("irelandie_missions.CountryPage", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        StreamFieldPanel("body"),
        MultiFieldPanel([
            ImageChooserPanel("image"),
            FieldPanel("image_alt"),
        ], heading="Image"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]


class RolePageIndex(Page, TranslatableMixin):
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

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        StreamFieldPanel("body"),
        PageChooserPanel("role_holder"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

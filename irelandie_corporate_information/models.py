# -*- coding: utf-8 -*-
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

from irelandie_missions.models import MissionPage

from .blocks import CorporateInformationPageSectionBlock


class CorportateInformationPageIndex(Page, TranslatableMixin):

    parent_page_types = [MissionPage]
    subpage_types = ["CorportateInformationPage"]
    max_count_per_parent = 1


class CorportateInformationPage(Page, TranslatableMixin):

    body = StreamField(
        [
            ("section", CorporateInformationPageSectionBlock()),
        ],
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True)

    parent_page_types = ["CorportateInformationPageIndex"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        StreamFieldPanel("body"),
    ]

# -*- coding: utf-8 -*-
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

from irelandie_missions.models import MissionPage

from .blocks import PressReleasePageSectionBlock


class PressReleasePageIndex(Page, TranslatableMixin):

    description = models.TextField(blank=True)

    parent_page_types = [MissionPage]
    subpage_types = ["PressReleasePage"]
    max_count_per_parent = 1

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class PressReleasePage(Page, TranslatableMixin):

    description = models.TextField(blank=True)
    body = StreamField(
        [
            ("section", PressReleasePageSectionBlock()),
        ],
        blank=True,
        null=True,
    )

    parent_page_types = [
        "PressReleasePageIndex",
    ]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        StreamFieldPanel("body"),
    ]

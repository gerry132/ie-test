# -*- coding: utf-8 -*-
from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from irelandie_missions.models import MissionPage
from irelandie_press_releases.blocks import PressReleasePageBlock
from irelandie_utils.models import BasePage, ArticlePage


class PressReleasePageIndex(BasePage):
    template = "patterns/pages/irelandie_press_releases/press_release_index.html"

    description = models.TextField(blank=True)

    parent_page_types = [MissionPage]
    subpage_types = ["PressReleasePage"]
    max_count_per_parent = 1

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class PressReleasePage(ArticlePage):
    template = "patterns/pages/irelandie_press_releases/press_release.html"

    override_related_articles = StreamField(
        [
            ("article", PressReleasePageBlock()),
        ],
        blank=True,
        max_num=3
    )

    parent_page_types = [
        "PressReleasePageIndex",
    ]
    subpage_types = []

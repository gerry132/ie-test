# -*- coding: utf-8 -*-
from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from irelandie_press_releases.blocks import PressReleasePageBlock
from irelandie_utils.models import BasePage, ArticlePage


class PressReleasePageIndex(BasePage):
    template = "patterns/pages/irelandie_press_releases/press_release_index.html"
    max_count_per_parent = 1

    description = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class PressReleasePage(ArticlePage):
    template = "patterns/pages/irelandie_press_releases/press_release_page.html"

    override_related_articles = StreamField(
        [
            ("article", PressReleasePageBlock()),
        ],
        blank=True,
        max_num=3
    )

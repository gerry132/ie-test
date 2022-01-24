# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from irelandie_missions.models import MissionPage
from irelandie_speeches.blocks import SpeechPageBlock
from irelandie_utils.models import BasePage, ArticlePage


class SpeechPageIndex(BasePage):

    description = models.TextField(blank=True)

    parent_page_types = [MissionPage]
    subpage_types = ["SpeechPage"]
    max_count_per_parent = 1

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class SpeechPage(ArticlePage):

    override_related_articles = StreamField(
        [
            ("article", SpeechPageBlock()),
        ],
        blank=True,
        max_num=3
    )

    parent_page_types = [
        "SpeechPageIndex",
    ]
    subpage_types = []

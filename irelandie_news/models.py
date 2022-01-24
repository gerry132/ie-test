# -*- coding: utf-8 -*-
from django import forms
from django.db import models

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

from irelandie_missions.models import MissionPage
from irelandie_news.blocks import NewsPageBlock
from irelandie_utils.models import ArticlePage, BasePage


class NewsPageIndex(BasePage):

    description = models.TextField(blank=True)

    parent_page_types = [MissionPage]
    subpage_types = ["NewsPage"]
    max_count_per_parent = 1

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class NewsPage(ArticlePage):

    countries = ParentalManyToManyField("irelandie_missions.CountryPage", blank=True)
    override_related_articles = StreamField(
        [
            ("article", NewsPageBlock()),
        ],
        blank=True,
        max_num=3
    )

    parent_page_types = [
        "NewsPageIndex",
    ]
    subpage_types = []

    content_panels = ArticlePage.content_panels + [
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]

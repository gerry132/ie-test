# -*- coding: utf-8 -*-
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from irelandie_news.blocks import NewsPageBlock
from irelandie_utils.models import ArticlePage, BasePage


class NewsPageIndex(BasePage):
    template = "patterns/pages/irelandie_news/news_index.html"
    max_count_per_parent = 1

    description = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class NewsPage(ArticlePage):
    template = "patterns/pages/irelandie_news/news_page.html"

    override_related_articles = StreamField(
        [
            ("article", NewsPageBlock()),
        ],
        blank=True,
        max_num=3
    )

# -*- coding: utf-8 -*-
from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from irelandie_publications.blocks import PublicationPageBlock
from irelandie_utils.models import BasePage, ArticlePage


class PublicationPageIndex(BasePage):
    template = "patterns/pages/irelandie_publications/publication_page.html"
    max_count_per_parent = 1

    description = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class PublicationPage(ArticlePage):
    template = "patterns/pages/irelandie_publications/publication_index.html"

    override_related_articles = StreamField(
        [
            ("article", PublicationPageBlock()),
        ],
        blank=True,
        max_num=3
    )

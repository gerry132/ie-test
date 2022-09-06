# -*- coding: utf-8 -*-
from functools import cached_property

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page

from irelandie_utils.models import MinimalArticlePage, BasePage


class NewsPageIndex(BasePage):
    template = "patterns/pages/irelandie_news/news_index.html"
    max_count_per_parent = 1

    description = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class NewsPage(MinimalArticlePage):
    template = "patterns/pages/irelandie_news/news_page.html"

    @cached_property
    def related_articles(self):
        return (
            NewsPage.objects.exact_type(type(self))
            .child_of(self.get_parent())
            .filter(locale=self.locale)
            .exclude(pk=self.pk)
            .public()
            .live()
            .order_by("publication_date")[:4]
            .specific()
        )

    class Meta:
        verbose_name = "News Content"

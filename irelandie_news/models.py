# -*- coding: utf-8 -*-
from functools import cached_property

from django.db import models
from wagtail.admin.panels import FieldPanel, StreamFieldPanel
from wagtail.models import Page
from wagtail.fields import StreamField
from irelandie_utils import blocks
import datetime

from irelandie_utils.models import MinimalArticlePage, BasePage


class NewsPageIndex(BasePage):
    template = "patterns/pages/irelandie_news/news_index.html"
    ajax_template = "patterns/molecules/article_card/ajax_article_card.html"
    description = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]

    @cached_property
    def related_articles(self, date=None):
        if not date:
            high_date = datetime.datetime.now()
            low_date = datetime.datetime(high_date.year, 1, 1)
        else:
            low_date = datetime.datetime(year, 1, 1)
            high_date = datetime.datetime(year, 12, 31)
        return (
            NewsPage.objects.child_of(self)
            .filter(publication_date__lte=high_date,
                    publication_date__gte=low_date,
                    locale=self.locale)
            .exclude(pk=self.pk)
            .public()
            .live()
            .order_by("publication_date")
            .specific()
        )


class NewsPage(MinimalArticlePage):
    template = "patterns/pages/irelandie_news/news_page.html"
    api_fields = [
        'publication_date',
        'hero_image',
        'introduction',
    ]

    @cached_property
    def related_articles(self):
        return (
            NewsPage.objects.exact_type(type(self))
            .child_of(self.get_parent())
            .filter(locale=self.locale, related_articles_active=True)
            .exclude(pk=self.pk)
            .public()
            .live()
            .order_by("publication_date")[:4]
            .specific()
        )

    class Meta:
        verbose_name = "News Content"


class NewsLandingPage(BasePage):
    template = "patterns/pages/irelandie_news/news_landing_page.html"
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    link_button = StreamField(
        [
            ("link_button", blocks.LinkButtonBlock()),
        ],
        blank=True,
        null=True,
    )
    content_panels = BasePage.content_panels + [
        StreamFieldPanel("generic_hero"),
        StreamFieldPanel("link_button")
    ]

    @cached_property
    def related_articles(self):
        return (
            NewsPage.objects.child_of(self.get_parent())
            .filter(locale=self.locale,
                    related_articles_active=True)
            .public()
            .live()
            .order_by("-publication_date")[:4]
            .specific()
        )

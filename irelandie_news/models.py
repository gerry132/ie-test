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
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    content_panels = Page.content_panels + [
        FieldPanel("description"),
        StreamFieldPanel("generic_hero", permission="access_admin"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if request.GET.get('year'):
            year = int(request.GET.get('year'))
            low_date = datetime.datetime(year, 1, 1)
            high_date = datetime.datetime(year, 12, 31)
        elif 'year' in request.GET:
            year = int(request.GET['year'])
            low_date = datetime.datetime(year, 1, 1)
            high_date = datetime.datetime(year, 12, 31)
        else:
            high_date = datetime.datetime.now()
            low_date = datetime.datetime(high_date.year, 1, 1)
        context['related_articles'] = (
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

        return context

    @cached_property
    def get_years(self):
        yearset = (NewsPage.objects.child_of(self)
                   .public()
                   .live()
                   .order_by()
                   .values('publication_date')
                   .distinct()
                   )
        year_list = []
        for year in yearset:
            if year['publication_date'].year not in year_list:
                year_list.append(year['publication_date'].year)
        return year_list


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
    parent_page_types = [
        'NewsPageIndex',
    ]
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

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['get_news_index'] = (
            NewsPageIndex.objects
            .public()
            .live()
            .specific()
        )
        return context

    @cached_property
    def get_years(self):
        yearset = (NewsPage.objects.child_of(self.get_parent())
                   .public()
                   .live()
                   .order_by()
                   .values('publication_date')
                   .distinct()
                   )
        year_list = []
        for year in yearset:
            if year['publication_date'].year not in year_list:
                year_list.append(year['publication_date'].year)
        return year_list

    @cached_property
    def get_root_index(self):
        return self.get_parent().url

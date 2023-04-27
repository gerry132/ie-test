# -*- coding: utf-8 -*-
from django.db import models
from irelandie_utils.models import BasePage

from irelandie_utils.blocks import StatsBlock, GenericHeroBlock

from .blocks import TagLandingBlock

from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel


class TagListPage(BasePage):
    subpage_types = [
        'TagPage'
    ]

    parent_page_types = [
        'irelandie_home.HomePage'
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        tag_pages = self.get_children().specific()
        context['tags'] = tag_pages
        return context


class TagPage(BasePage):
    tag_label = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("tag_label"),
    ]


class TagLandingPage(BasePage):
    template = "patterns/pages/irelandie_pages/free_form_page.html"
    generic_hero = StreamField(
        [
            ("generic_hero", GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    body = StreamField(
        [
            ("content", TagLandingBlock())
        ],
        blank=True
    )

    stats_block = StreamField(
        [
            ("content", StatsBlock())
        ],
        blank=True,
        max_num=2
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("generic_hero",  heading="Mini Hero Block"),
        FieldPanel("body"),
        FieldPanel("stats_block"),
        InlinePanel('page_related_tags', max_num=1, label="Tag"),
    ]

    def get_context(self, request, *args, **kwargs):
        # from irelandie_pages.models import FreeFormPage
        tags = TagPage.objects.live()
        context = super().get_context(request, *args, **kwargs)
        context['tags'] = tags
        # obj = TagPage.objects.get(pk=7)
        # f = FreeFormPage.objects.live().filter(page_related_tags__page=obj)
        # print(f)
        return context

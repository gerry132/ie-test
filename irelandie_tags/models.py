# -*- coding: utf-8 -*-
from functools import cached_property

from django.db import models

from irelandie_utils.models import BasePage

from irelandie_utils.blocks import GenericHeroBlock, StatTagBlock
from irelandie_utils.utils import get_root_info

from .blocks import TagLandingBlock

from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel

from itertools import chain
from operator import attrgetter


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
    parent_page_types = [
        'TagListPage'
    ]
    tag_label = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("tag_label"),
    ]


class TagLandingPage(BasePage):
    template = "patterns/pages/irelandie_tags/tag_landing_page.html"
    generic_hero = StreamField(
        [
            ("generic_hero", GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    body = StreamField(TagLandingBlock(), blank=True)

    stats_block = StreamField(
        [
            ("content", StatTagBlock())
        ],
        blank=True,
        max_num=2
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("generic_hero", heading="Mini Hero Block"),
        FieldPanel("body"),
        FieldPanel("stats_block"),
        InlinePanel('page_related_tags', min_num=1, max_num=1, label="Tag"),
    ]

    def get_context(self, request, *args, **kwargs):
        """
        In the context we run 3 queries to
        return the most recently published
        story objects.
        """
        from irelandie_pages.models import FreeFormPage
        from irelandie_story.models import StoryPage
        from irelandie_missions.models import GeneralContentPage
        from irelandie_home.models import HomePage

        tag = self.related_tags[0]

        context = super().get_context(request, *args, **kwargs)

        freeform = FreeFormPage.objects.live().filter(locale=self.locale, page_related_tags__page=tag).specific()
        stories = StoryPage.objects.live().filter(locale=self.locale, page_related_tags__page=tag).specific()
        general_content = GeneralContentPage.objects.live().filter(
            locale=self.locale, page_related_tags__page=tag).specific()
        print(freeform, stories)
        results = sorted(
            chain(stories, freeform, general_content),
            key=attrgetter('last_published_at')
        )[:9]

        context['stories'] = results
        pages = self.get_ancestors()
        context, root_found = get_root_info(context, pages)
        if not root_found:
            f = HomePage.objects.all()[:1].get()
            context['default_image'] = f.default_image
        return context

    @cached_property
    def get_root_index(self):
        if self.get_first_child():
            return self.get_first_child().url

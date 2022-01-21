# -*- coding: utf-8 -*-
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from irelandie_utils import blocks
from irelandie_utils.models import HeroPage


class HomePage(HeroPage):

    #

    stories = StreamField(
        [
            ('story', blocks.StoryBlock())
        ],
        min_num=0,
        max_num=1,
        blank=True,
        null=True,
    )

    pinned_stories = StreamField(
        [
            ('pinned_story', blocks.PinnedStoryBlock())
        ],
        min_num=0,
        max_num=4,
        blank=True,
        null=True,
    )

    #

    max_count = 1
    template = 'patterns/pages/home/home_page.html'

    #

    # Only allow creating HomePages at the root level
    parent_page_types = ['wagtailcore.Page']
    subpage_types = [
        'irelandie_missions.CountryGroupPageIndex'
    ]

    #

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel('stories'),
        StreamFieldPanel('pinned_stories'),
    ]

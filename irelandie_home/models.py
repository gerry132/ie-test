# -*- coding: utf-8 -*-
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from irelandie_utils import blocks
from irelandie_utils.models import HeroPage


class HomePage(HeroPage):
    template = "irelandie_assets/pages/home.html"

    # Only allow creating HomePages at the root level
    parent_page_types = ["wagtailcore.Page"]

    stories = StreamField(
        [("story", blocks.StoryBlock())],
        min_num=0,
        blank=True,
        null=True,
        help_text="Move a story to the top of this list to promote it as the main story"
    )
    pinned_stories = StreamField(
        [("pinned_story", blocks.PinnedStoryBlock())],
        min_num=0,
        blank=True,
        null=True,
    )

    max_count = 1
    subpage_types = ["irelandie_missions.CountryGroupPageIndex"]

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel("stories"),
        StreamFieldPanel("pinned_stories"),
    ]

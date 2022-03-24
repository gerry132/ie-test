# -*- coding: utf-8 -*-
from wagtail.admin.edit_handlers import TabbedInterface, ObjectList, StreamFieldPanel
from wagtail.core import blocks as wagtail_blocks
from wagtail.core.fields import StreamField
from irelandie_home.blocks import SecondaryCallToAction

from irelandie_utils import blocks
from irelandie_utils.models import HeroPage
from irelandie_pages.models import FreeFormPageBase


class HomePage(FreeFormPageBase):
    max_count = 1
    template = "patterns/pages/home/home_page.html"

    secondary_call_to_action = StreamField(
        [
            ("call_to_action", SecondaryCallToAction()),
        ],
        blank=True,
    )

    cta_panel = [
        StreamFieldPanel("secondary_call_to_action")

    ]
    # Only allow creating HomePages at the root level
    parent_page_types = ["wagtailcore.Page"]

    edit_handler = TabbedInterface([
        ObjectList(FreeFormPageBase.content_panels, heading='Content'),
        ObjectList(FreeFormPageBase.hero_panel, heading='Hero'),
        ObjectList(cta_panel, heading='Call To Action'),
        ObjectList(FreeFormPageBase.promote_panels, heading='Promote'),
        ObjectList(FreeFormPageBase.settings_panels, heading='Settings', classname="settings"),
    ])


class CampaignPage(HeroPage):
    top_stories = StreamField(
        [("story", blocks.StoryBlock())],
        min_num=0,
        max_num=1,
        blank=True,
        null=True,
    )

    embeds = StreamField(
        [
            ("youtube", blocks.YoutubeVideoBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    pinned_stories = StreamField(
        [
            (
                "pinned_story",
                wagtail_blocks.StructBlock(
                    [
                        ("pinned_story_hero", blocks.PinnedStoryHeroBlock()),
                        (
                            "pinned_stories",
                            wagtail_blocks.ListBlock(blocks.PinnedStoryBlock()),
                        ),
                    ],
                    template="patterns/molecules/pinned-stories/pinned_stories.html",
                ),
            ),
        ],
        block_counts={
            "pinned_story": {"max_num": 1},
        },
        blank=True,
        null=True,
    )

    secondary_stories = StreamField(
        [("story", blocks.StoryBlock())],
        min_num=0,
        blank=True,
        null=True,
    )

    template = "patterns/pages/home/campaign_page.html"

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel("top_stories"),
        StreamFieldPanel("embeds"),
        StreamFieldPanel("pinned_stories"),
        StreamFieldPanel("secondary_stories"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel, heading='Hero'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])


class TopicPage(HeroPage):
    template = "patterns/pages/home/topic_page.html"

    body = StreamField(
        [
            (
                "rich_text",
                wagtail_blocks.RichTextBlock(
                    features=["h3", "blockquote", "bold", "link", "document-link", "ul"]
                ),
            ),
        ],
        blank=True,
        null=True,
    )

    featured_articles = StreamField(
        [("featured_articles", blocks.FeaturedArticlesBlock())],
        blank=True,
        null=True,
        max_num=1,
    )

    articles = StreamField(
        [("articles", blocks.ArticleCardsBlock())],
        blank=True,
        max_num=1,
    )
    embeds = StreamField(
        [
            ("youtube", blocks.YoutubeVideoBlock()),
        ],
        blank=True,
        max_num=1,
    )

    logo_cards = StreamField(
        [("logo_cards", blocks.LogoCardsBlock())],
        blank=True,
        max_num=1,
    )

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel("body"),
        StreamFieldPanel("featured_articles"),
        StreamFieldPanel("articles", heading="Article Cards"),
        StreamFieldPanel("embeds"),
        StreamFieldPanel("logo_cards", heading="Logo Cards"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel, heading='Hero'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])

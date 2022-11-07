# -*- coding: utf-8 -*-
from functools import cached_property
from django.db import models
from wagtail.admin.panels import TabbedInterface, ObjectList, StreamFieldPanel, FieldPanel
from wagtail import blocks as wagtail_blocks
from wagtail.fields import StreamField
from irelandie_home.blocks import SecondaryCallToAction
from irelandie_news.models import NewsPage

from irelandie_utils import blocks
from irelandie_utils.models import HeroPage
from irelandie_pages.models import FreeFormPageBase
from wagtail.images import get_image_model_string

IMAGE_MODEL = get_image_model_string()


class HomePage(FreeFormPageBase):
    max_count = 1
    template = "patterns/pages/home/home_page.html"
    favicon = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    top_story = StreamField(
        [
            ("story", blocks.TopStoryBlock()),
        ],
        blank=True,
        block_counts={
            "story": {"max_num": 1},
        }
    )

    promote_panels = FreeFormPageBase.promote_panels + [
        StreamFieldPanel("top_story"),
    ]
    settings_panels = ([
        FieldPanel("favicon", permission="access_admin"),
    ]) + FreeFormPageBase.settings_panels

    secondary_call_to_action = StreamField(
        [
            ("call_to_action", SecondaryCallToAction()),
        ],
        blank=True,
    )

    secondary_cta_panel = [
        StreamFieldPanel("secondary_call_to_action")

    ]
    # Only allow creating HomePages at the root level
    parent_page_types = ["wagtailcore.Page"]

    edit_handler = TabbedInterface([
        ObjectList(FreeFormPageBase.content_panels, heading='Content'),
        ObjectList(FreeFormPageBase.hero_panel, heading='Hero'),
        ObjectList(secondary_cta_panel, heading='Call To Action'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])

    @cached_property
    def home_articles(self):
        return (
            NewsPage.objects.filter(locale=self.locale, featured_home=True)
            .exclude(pk=self.pk)
            .public()
            .live()
            .order_by("-publication_date")[:4]
            .specific()
        )


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

    # TODO: would benefit from it's own PinnedStoriesBlock to simplify the template.
    # issue https://github.com/ogcio/ireland-ie-wagtail/issues/293
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
        StreamFieldPanel("top_stories", heading="Two Column Feature"),
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
                blocks.RichTextBlock(),
            ),
            (
                "rich_text_advanced",
                blocks.AdvancedRichTextBlock(),
            ),
            (
                "articles",
                blocks.ArticleCardsBlock()
            ),
            (
                "logo_cards",
                blocks.LogoCardsBlock()
            ),
            (
                "link_cards",
                blocks.LinkCardsBlock()
            ),
            (
                "youtube",
                blocks.YoutubeVideoBlock()
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

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel("body"),
        StreamFieldPanel("featured_articles"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel, heading='Hero'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from irelandie_missions.models import MissionPage
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = MissionPage.objects.live().get(id=p.id)
                if missions.root_page:
                    context['default_image'] = missions.default_image
        return context

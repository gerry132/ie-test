# -*- coding: utf-8 -*-
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core import blocks as wagtail_blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from irelandie_utils import blocks
from irelandie_utils.models import HeroPage


class HomePage(HeroPage):

    #

    top_stories = StreamField(
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
            ('pinned_story_hero', blocks.PinnedStoryHeroBlock()),
            ('pinned_story', blocks.PinnedStoryBlock()),
        ],
        block_counts={
            'pinned_story_hero': {'max_num': 1},
        },
        min_num=0,
        blank=True,
        null=True,
    )

    secondary_stories = StreamField(
        [
            ('story', blocks.StoryBlock())
        ],
        min_num=0,
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
        'irelandie_missions.CountryGroupPageIndex',
        'irelandie_missions.MissionSearchPage',
        'irelandie_home.CampaignPage',
        'irelandie_home.TopicPage',
    ]

    #

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel('top_stories'),
        StreamFieldPanel('pinned_stories'),
        StreamFieldPanel('secondary_stories'),
    ]


class CampaignPage(HeroPage):
    top_stories = StreamField(
        [
            ('story', blocks.StoryBlock())
        ],
        min_num=0,
        max_num=1,
        blank=True,
        null=True,
    )

    embeds = StreamField(
        [
            ('youtube', blocks.YoutubeVideoBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    pinned_stories = StreamField(
        [
            ('pinned_story_hero', blocks.PinnedStoryHeroBlock()),
            ('pinned_story', blocks.PinnedStoryBlock()),
        ],
        block_counts={
            'pinned_story_hero': {'max_num': 1},
        },
        min_num=0,
        blank=True,
        null=True,
    )

    secondary_stories = StreamField(
        [
            ('story', blocks.StoryBlock())
        ],
        min_num=0,
        blank=True,
        null=True,
    )


    template = 'patterns/pages/home/campaign_page.html'

    parent_page_types = ['irelandie_home.HomePage']
    subpage_types = []

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel('top_stories'),
        StreamFieldPanel('embeds'),
        StreamFieldPanel('pinned_stories'),
        StreamFieldPanel('secondary_stories'),
    ]


class TopicPage(HeroPage):
    body = StreamField(
        [
            (
                'rich_text',
                wagtail_blocks.RichTextBlock(
                    features=["h3", "blockquote", "bold", "link", "document-link", "ul"]
                ),
            ),
        ],
        blank=True,
        null=True,
    )
    featured_articles = StreamField(
        [
            (
                'article',
                wagtail_blocks.PageChooserBlock(
                    page_type=[
                        'irelandie_corporate_information.CorportateInformationPage',
                        'irelandie_news.NewsPage',
                        'irelandie_press_releases.PressReleasePage',
                        'irelandie_publications.PublicationPage',
                        'irelandie_speeches.SpeechPage',
                        'irelandie_site_information.SiteInformationPage',
                    ]
                )
            ),
        ],
        blank=True,
        null=True,
    )


    template = 'patterns/pages/home/topic_page.html'

    parent_page_types = ['irelandie_home.HomePage']
    subpage_types = []

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel('body'),
        StreamFieldPanel('featured_articles'),
    ]

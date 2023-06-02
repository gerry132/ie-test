# -*- coding: utf-8 -*-
from django.db import models
from irelandie_utils.blocks import AdvancedRichTextBlock, LinkBoxesBlock, LinkCardsBlock

from irelandie_utils.models import BasePage
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.blocks import SnippetChooserBlock

from wagtail.blocks import PageChooserBlock

from .blocks import TravelCautionBlock, ButtonBlock, InformationBlock, TravelRegionBlock, TravelIndexOuterBlockBool

from irelandie_utils.blocks import AccordionBlock


class TravelCountryPage(BasePage):
    template = "patterns/pages/irelandie_travel/travel_country.html"
    subtitle = StreamField(
        [
            ('subtitle', AdvancedRichTextBlock()),
            ("travel_snippet", SnippetChooserBlock(target_model="utils.TravelSnippet"))
        ],
        null=True,
        blank=False
    )

    region = StreamField(
        [
            ('region', TravelRegionBlock())
        ],
        max_num=1,
        null=True,
        blank=False
    )

    travel_caution_level = StreamField(
        [
            ('security_status', TravelCautionBlock())
        ],
        max_num=1,
        null=True,
        blank=False
    )

    body = StreamField(
        [
            ("accordions", AccordionBlock()),
        ],
        blank=True,
        null=True,
    )

    outer_body = StreamField(
        [
            ('information', InformationBlock()),
            ('button', ButtonBlock()),
            ("travel_snippet", SnippetChooserBlock(target_model="utils.TravelSnippet"))
        ],
        blank=True,
        null=True
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('region'),
        FieldPanel('travel_caution_level', heading="Security Status"),
        FieldPanel('body'),
        FieldPanel('outer_body'),
    ]


class TravelLandingPage(BasePage):
    template = "patterns/pages/irelandie_travel/travel_landing.html"
    body = StreamField(
        [
            ("advanced_rich_text", AdvancedRichTextBlock()),
            ("link_buttons", LinkBoxesBlock()),
            ("link_cards", LinkCardsBlock()),
        ],
        blank=True
    )
    advanced_rich_text = StreamField(
        [
            ("advanced_rich_text", AdvancedRichTextBlock()),
        ],
        blank=True
    )
    twitter_title = models.CharField(max_length=50, blank=True)

    twitter_username = models.CharField(max_length=100, blank=True)
    content_panels = BasePage.content_panels + [
        FieldPanel('body'),
        FieldPanel('advanced_rich_text'),
        MultiFieldPanel([
            FieldPanel("twitter_title"),
            FieldPanel("twitter_username"),
        ], heading="Twitter feed"),
    ]


class TravelIndexPage(BasePage):
    template = "patterns/pages/irelandie_travel/travel_index.html"
    subtitle = StreamField(
        [
            ('subtitle', AdvancedRichTextBlock()),
        ],
        null=True,
        blank=True
    )

    quick_links = StreamField(
        [
            ('travel_page', PageChooserBlock(
                required=False,
                page_type=[
                    "irelandie_travel.TravelCountryPage",
                    "irelandie_travel.TravelLandingPage"
                    ]
                )
             ),
        ],
        null=True,
        blank=True,
        max_num=8
    )

    body = StreamField(
        [
            ('travel_index_block', TravelIndexOuterBlockBool())
        ],
        null=True,
        blank=True
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('quick_links'),
        FieldPanel('body'),
    ]

    subpage_types = [
        'TravelCountryPage',
        'TravelLandingPage'
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        travel_pages = TravelCountryPage.objects.all().order_by('title')
        alpha_map = {
            'A': [], 'B': [], 'C': [],
            'D': [], 'E': [], 'F': [],
            'G': [], 'H': [], 'I': [],
            'J': [], 'K': [], 'L': [],
            'M': [], 'N': [], 'O': [],
            'P': [], 'Q': [], 'R': [],
            'S': [], 'T': [], 'U': [],
            'V': [], 'W': [], 'X': [],
            'Y': [], 'Z': []
        }

        for page in travel_pages:
            alpha_map[page.title[0]].append(page)

        context['travel_pages'] = alpha_map
        return context

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

from django.core.exceptions import ValidationError
from urllib.parse import urlparse


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


def validate_hostname(value):
    if not value:
        return  # Required error is done the field
    obj = urlparse(value)
    if obj.hostname == 'twitter.com':
        raise ValidationError(f'Only add the social media handle here, e.g. if the full link is '
                              f'https://{obj.hostname}/myprofile, type myprofile into this box.')


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

    twitter_username = models.CharField(max_length=100, blank=True, validators=[validate_hostname])
    root_page = models.BooleanField(default=True)
    content_panels = BasePage.content_panels + [
        FieldPanel('body'),
        FieldPanel('advanced_rich_text'),
        MultiFieldPanel([
            FieldPanel("twitter_title"),
            FieldPanel("twitter_username"),
        ], heading="Twitter feed"),
    ]
    settings_panels = (
        [
            FieldPanel("root_page", permission="access_admin"),
        ] +
        BasePage.settings_panels

    )


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
        travel_pages = TravelCountryPage.objects.filter(locale=self.locale).live().order_by('title')
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
            if self.locale.language_code == 'ga' and page.title[:2] == 'An' and page.title[3].islower():
                alpha_map[page.title[4]].append(page)
            elif self.locale.language_code == 'ga' and page.title[:2] == 'An':
                alpha_map[page.title[3]].append(page)
            else:
                alpha_map[page.title[0]].append(page)

        context['travel_pages'] = alpha_map
        return context

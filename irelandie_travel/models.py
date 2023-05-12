from irelandie_utils.blocks import AdvancedRichTextBlock

from irelandie_utils.models import BasePage

from .blocks import TravelCautionBlock, ButtonBlock, InformationBlock, TravelRegionBlock

from irelandie_utils.blocks import AccordionBlock
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel


class TravelIndexPage(BasePage):
    pass


class TravelCountryPage(BasePage):
    template = "patterns/pages/irelandie_travel/travel_country.html"
    subtitle = StreamField(
        [
            ('subtitle', AdvancedRichTextBlock())
        ],
        max_num=1,
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
            ('travel_caution_level', TravelCautionBlock())
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
        ],
        blank=True,
        null=True
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('region'),
        FieldPanel('travel_caution_level'),
        FieldPanel('body'),
        FieldPanel('outer_body'),
    ]


class TravelLandingPage(BasePage):
    pass

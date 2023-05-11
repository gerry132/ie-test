from django.db import models

from irelandie_utils.models import BasePage
from irelandie_utils.constants import TravelRegions, TravelCautionLevel

from .blocks import TravelCountryPageBlock, ButtonBlock, InformationBlock, RelatedLinksBlock

from wagtail import blocks
from wagtail.fields import StreamField


class TravelIndexPage(BasePage):
    pass


class TravelCountryPage(BasePage):
    subtitle = models.CharField(max_length=100,
                                null=True,
                                blank=True)

    region = blocks.ChoiceBlock(
        required=True,
        choices=TravelRegions.choices,
        default=TravelRegions.ASIA_AND_OCEANIA,
    )

    travel_caution_level = blocks.ChoiceBlock(
        required=True,
        choices=TravelCautionLevel.choices,
        default=TravelCautionLevel.NORMAL_PRECAUTIONS
    )

    body = StreamField(
         [
             ('travel', TravelCountryPageBlock()),
         ],
         blank=True,
         null=True
     )

    outer_body = StreamField(
        [
            ('information', InformationBlock()),
            ('button', ButtonBlock()),
            ('related_link', RelatedLinksBlock())
        ],
        blank=True,
        null=True
    )


class TravelLandingPage(BasePage):
    pass

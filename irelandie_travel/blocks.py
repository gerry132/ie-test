from irelandie_home.blocks import SecondaryCallToAction
from irelandie_utils.blocks import GeneralContentBlocks, AdvancedRichTextBlock, LinkButtonBlock, ImageChooserBlock
from wagtail import blocks

from irelandie_utils.constants import TravelCautionLevel, TravelRegions


class TravelCountryPageBlock(blocks.StructBlock):
    title = blocks.CharBlock(blank=False)
    general_contents = GeneralContentBlocks(blank=True)


class AlteredAvancedRichTextBlock(AdvancedRichTextBlock):
    button_links = blocks.StreamBlock(
        [
            ("button", SecondaryCallToAction())
        ],
        blank=True,
        min_num=0,
        required=False,
    )


class InformationBlock(blocks.StreamBlock):

    richtext = AlteredAvancedRichTextBlock()


class ButtonBlock(blocks.StreamBlock):
    button = LinkButtonBlock()
    image = ImageChooserBlock()


class TravelCautionBlock(blocks.StructBlock):
    travel_caution_level = blocks.ChoiceBlock(
        required=True,
        choices=TravelCautionLevel.choices,
        default=TravelCautionLevel.NORMAL_PRECAUTIONS
    )


class TravelRegionBlock(blocks.StructBlock):
    region = blocks.ChoiceBlock(
        required=True,
        choices=TravelRegions.choices,
        default=TravelRegions.ASIA_AND_OCEANIA,
    )

from irelandie_utils.blocks import GeneralContentBlocks, AdvancedRichTextBlock, LinkButtonBlock, ImageChooserBlock
from wagtail import blocks


class TravelCountryPageBlock(GeneralContentBlocks):
    title = blocks.CharBlock(blank=False)


class InformationBlock(blocks.StreamBlock):
    richtext = AdvancedRichTextBlock()


class ButtonBlock(blocks.StreamBlock):
    button = LinkButtonBlock()
    image = ImageChooserBlock()


class RelatedLinksBlock(blocks.StreamBlock):
    richtext = AdvancedRichTextBlock()

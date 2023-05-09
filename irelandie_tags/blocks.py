from irelandie_utils.blocks import (
    AdvancedRichTextBlock,
    StoryBlock,
)

from wagtail import blocks


class TagLandingBlock(blocks.StreamBlock):
    rich_text = AdvancedRichTextBlock(group="Base")
    two_column_feature = StoryBlock()

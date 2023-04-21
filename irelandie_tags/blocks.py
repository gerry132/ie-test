from irelandie_utils.blocks import (
    AdvancedRichTextBlock,
    StatsBlock,
    FeaturedStoryBlock,
)

from wagtail import blocks


class TagLandingBlock(blocks.StreamBlock):
    rich_text = AdvancedRichTextBlock(group="Base")
    stats_block = StatsBlock(limit=2)
    two_column_feature = FeaturedStoryBlock()

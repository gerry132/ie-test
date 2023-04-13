from irelandie_utils.blocks import (
    AdvancedRichTextBlock,
    ImageBlock,
    TableBlock,
    VideoBlock,
    AccordionBlock,
    StatsBlock,
    StoryPhotoGalleriesBlock,
    TimelinePhotoGalleriesBlock,
    FeaturedStoryBlock,
    LinkCardsBlock,
    MultimediaRowBlock,
    LogoCardsBlock,
    ArticleCardsBlock,
    DocumentBlock
)

from wagtail import blocks


class StoryPageBlock(blocks.StreamBlock):
    rich_text = AdvancedRichTextBlock(group="Base")
    image = ImageBlock(group="Base")
    document = DocumentBlock(group="Base")
    html = blocks.RawHTMLBlock(
        group="HTML",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
    )
    table = TableBlock(table_options={'renderer': 'html'}, group="HTML")
    video = VideoBlock(group="Base")
    accordion = AccordionBlock(group="Base")
    logos = LogoCardsBlock(group="Base")
    stats_block = StatsBlock(group="Base")
    story_photo_gallery = StoryPhotoGalleriesBlock(group="Base")
    timeline_photo_gallery = TimelinePhotoGalleriesBlock(group="Base")
    two_column_feature = FeaturedStoryBlock(group="Module")
    link_cards = LinkCardsBlock(group="Module")
    stats_block = StatsBlock(group="Base")
    multimedia_row = MultimediaRowBlock(group="Base")
    logo_cards = LogoCardsBlock(group="Module")

    articles = ArticleCardsBlock(group="Module")

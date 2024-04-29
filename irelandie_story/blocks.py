from irelandie_utils.blocks import (
    AdvancedRichTextBlock,
    ImageBlock,
    TableBlock,
    AccordionBlock,
    StatsBlock,
    StoryPhotoGalleriesBlock,
    TimelinePhotoGalleriesBlock,
    LinkCardsBlock,
    MultimediaRowBlock,
    LogoCardsBlock,
    ArticleCardsBlock,
    DocumentBlock, FeaturedTaggedStoriesBlock, StoryBlock, StoryVideoBlock, OverviewPullOutTextBlock,
    PolicyDocumentBoxBlock, InfoAtAGlanceBlock
)

from wagtail import blocks


class StoryPageBlock(blocks.StreamBlock):
    rich_text = AdvancedRichTextBlock(group="Base")
    image = ImageBlock(group="Base")
    document = DocumentBlock(group="Base")
    html = blocks.RawHTMLBlock(
        group="HTML",
        help_text="Add title attribute value to iframe for accessibility.",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
    )
    table = TableBlock(table_options={'renderer': 'html'}, group="HTML")
    video = StoryVideoBlock(group="Base")
    accordion = AccordionBlock(group="Base")
    logos = LogoCardsBlock(group="Base")
    stats_block = StatsBlock(group="Base")
    story_photo_gallery = StoryPhotoGalleriesBlock(group="Base")
    timeline_photo_gallery = TimelinePhotoGalleriesBlock(group="Base")
    overview_pull_out_textblock = OverviewPullOutTextBlock(group="Base")
    policy_document_box = PolicyDocumentBoxBlock(group="Base")
    info_at_a_glance = InfoAtAGlanceBlock(group="Base")
    two_column_feature = StoryBlock(group="Module")
    link_cards = LinkCardsBlock(group="Module")
    Featured_tagged_story = FeaturedTaggedStoriesBlock(group="Module")
    multimedia_row = MultimediaRowBlock(group="Base")
    logo_cards = LogoCardsBlock(group="Module")

    articles = ArticleCardsBlock(group="Module")

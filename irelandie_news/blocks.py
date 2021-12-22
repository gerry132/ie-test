# -*- coding: utf-8 -*-
from wagtail.core import blocks as wagtail_blocks

from irelandie_utils import blocks


class NewsPageSectionBlock(blocks.BaseSectionBlock):
    class Meta:
        label = "SectionBlock"
        template = "TODO"

    body = wagtail_blocks.StreamBlock(
        [
            ("contact_detail", blocks.ContactDetailBlock()),
            ("document", blocks.DocumentBlock()),
            ("image", blocks.ImageBlock()),
            ("place", blocks.PlaceBlock()),
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=["h3", "blockquote", "bold", "link", "document-link", "ul"]
                ),
            ),
            ("table", blocks.TableBlock()),
            ("youtube_video", blocks.YoutubeVideoBlock()),
        ],
        required=False,
    )

# -*- coding: utf-8 -*-
from wagtail.core import blocks as wagtail_blocks

from irelandie_utils import blocks


class PressReleasePageSectionBlock(blocks.BaseSectionBlock):
    class Meta:
        label = "SectionBlock"
        template = "TODO"

    body = wagtail_blocks.StreamBlock(
        [
            ("document", blocks.DocumentBlock()),
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=["h3", "blockquote", "bold", "link", "document-link", "ul"]
                ),
            ),
            ("table", blocks.TableBlock()),
        ],
        required=False,
    )

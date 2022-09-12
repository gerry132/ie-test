# -*- coding: utf-8 -*-
from wagtail import blocks as wagtail_blocks

from irelandie_utils import blocks


class PlacePageSectionBlock(blocks.BaseSectionBlock):
    class Meta:
        label = "SectionBlock"
        template = "TODO"

    body = wagtail_blocks.StreamBlock(
        [
            ("contact_detail", blocks.ContactDetailBlock()),
            ("document", blocks.DocumentBlock()),
            ("person", blocks.PersonBlock()),
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=["h3", "blockquote", "bold", "link", "document-link", "ul"]
                ),
            ),
            ("role", blocks.RoleBlock()),
            ("table", blocks.TableBlock()),
        ],
        required=False,
    )

# -*- coding: utf-8 -*-
from wagtail.core import blocks as wagtail_blocks

from irelandie_utils import blocks


class PersonPageSectionBlock(blocks.BaseSectionBlock):
    class Meta:
        label = "SectionBlock"
        template = "TODO"

    body = wagtail_blocks.StreamBlock(
        [
            ("contact_detail", blocks.ContactDetailBlock()),
            ("place", blocks.PlaceBlock()),
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=["h3", "blockquote", "bold", "link", "document-link", "ul"]
                ),
            ),
            ("role", blocks.RoleBlock()),
        ],
        required=False,
    )


class RolePageSectionBlock(blocks.BaseSectionBlock):
    class Meta:
        label = "SectionBlock"
        template = "TODO"

    body = wagtail_blocks.StreamBlock(
        [
            ("contact_detail", blocks.ContactDetailBlock()),
            ("person", blocks.PersonBlock()),
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=["h3", "blockquote", "bold", "link", "document-link", "ul"]
                ),
            ),
        ],
        required=False,
    )

# -*- coding: utf-8 -*-
from wagtail.core import blocks as wagtail_blocks
from wagtail.images.blocks import ImageChooserBlock

from irelandie_utils import blocks
from irelandie_utils.blocks import StoryLinkBlock


class PersonPageSectionBlock(blocks.BaseSectionBlock):
    class Meta:
        label = "SectionBlock"
        template = "TODO"

    image = ImageChooserBlock()
    # TODO not implementing this yet
    # image_alt = wagtail_blocks.CharBlock(required=False)
    page = wagtail_blocks.PageChooserBlock(required=False)

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

    links = wagtail_blocks.StreamBlock(
        [
            ('link', StoryLinkBlock()),
        ],
        max_num=3,
        min_num=0,
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

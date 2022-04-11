# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

from wagtail.core import blocks
from irelandie_utils.blocks import BaseBlockLinkValidation, BaseBlockLinkContext


class LinkBlock(BaseBlockLinkContext):
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text=_("Leave blank to use the page's own title"), required=False
    )

    class Meta:
        template = ("patterns/molecules/navigation/blocks/menu_item.html",)


class LinkBlockExtended(LinkBlock, BaseBlockLinkContext, BaseBlockLinkValidation):
    # This is a custom block that extends the LinkBlock and adds a url field.
    # This is used in PrimaryNavigation() & FooterNavigation()
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )

    class Meta:
        template = ("patterns/molecules/navigation/blocks/menu_item_extended.html",)


class LinkColumnWithHeader(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=False, help_text=_("Leave blank if no header required.")
    )
    links = blocks.ListBlock(LinkBlockExtended())

    class Meta:
        template = ("patterns/molecules/navigation/blocks/footer_column.html",)


class SecondaryNavLinkColumnWithHeader(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=False, help_text=_("Leave blank if no header required.")
    )
    links = blocks.ListBlock(LinkBlockExtended())

    class Meta:
        template = ("patterns/molecules/navigation/blocks/secondary_nav_column.html",)

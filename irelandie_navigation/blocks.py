# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from irelandie_utils.blocks import BaseBlockLinkValidation, BaseBlockLinkContext, AdvancedRichTextBlock, ImageBlock, \
    ALT_IMAGE


class LinkBlock(BaseBlockLinkContext):
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text=_("Leave blank to use the page's own title"), required=False
    )

    class Meta:
        template = ("patterns/molecules/navigation/blocks/menu_item.html",)


class MegaMenu(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    sub_text = blocks.CharBlock(required=False)
    mega_menu_links = blocks.StreamBlock([
        ("mega_menu", LinkBlock()),
    ],
        required=False, )
    richtext = blocks.StreamBlock([
        ("advanced_rich_text", AdvancedRichTextBlock()),
        (
            "image_rich_text",
            blocks.StructBlock(
                [
                    ("image", ImageChooserBlock(required=True)),
                    ("image_alt", blocks.CharBlock(
                        required=True,
                        help_text=_(ALT_IMAGE),
                    )),
                    ("page", blocks.PageChooserBlock(required=False)),
                    ("url", blocks.URLBlock(
                        label="URL",
                        required=False,
                        help_text="An external link.",
                    )),
                ],
                icon="link",
            ),
        ),
    ],
        required=False,
        blank=True,
        max_num=3,
        min_num=0, )
    image = blocks.StreamBlock([
        ("image", ImageBlock()),
    ],
        required=False,
        blank=True,
        max_num=1,
        min_num=0,
    )


class LinkBlockExtendedwithMegaMenu(LinkBlock, BaseBlockLinkContext, BaseBlockLinkValidation):
    # This is a custom block that extends the LinkBlock and adds a url field.
    # This is used in PrimaryNavigation() & FooterNavigation()
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )
    mega_menu = blocks.StreamBlock([("mega_menu", MegaMenu())],
                                   required=False, blank=True,
                                   max_num=1,
                                   min_num=0, )

    class Meta:
        template = ("patterns/molecules/navigation/blocks/menu_item_with_megamenu.html",)


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


class NoticeBarWithMessageLink(LinkBlockExtended):
    title = blocks.CharBlock(
        help_text=_("Leave blank to use the page's own title as a message"),
        required=False,
        max_length=80,
    )

    enable = blocks.BooleanBlock(
        required=False,
        default=False,
    )

    class Meta:
        template = ("patterns/molecules/notice-bar/blocks/notice_bar.html",)

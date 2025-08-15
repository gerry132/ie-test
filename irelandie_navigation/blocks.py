# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from irelandie_home.blocks import SecondaryCallToAction

from irelandie_utils.blocks import BaseBlockLinkValidation, BaseBlockLinkContext, AdvancedRichTextBlock, ImageBlock, \
    ALT_IMAGE
from django.forms.utils import ErrorList
from wagtail.blocks.struct_block import StructBlockValidationError


class LinkBlock(BaseBlockLinkContext):
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text=_("Leave blank to use the page's own title"), required=False
    )

    class Meta:
        template = ("patterns/molecules/navigation/blocks/menu_item.html",)


class LinkBlockWithURL(BaseBlockLinkContext, BaseBlockLinkValidation):
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text=_("Leave blank to use the page's own title"), required=False
    )
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )


class LinkWithURLANDSubLinks(BaseBlockLinkContext, BaseBlockLinkValidation):
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text=_("Leave blank to use the page's own title"), required=False
    )
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )
    mega_menu_sub_links = blocks.StreamBlock([
        ("mega_menu_sub_links", LinkBlockWithURL()),
    ],
        required=False,
        blank=True,
    )


class MegaMenuContent(blocks.StructBlock):
    mega_menu_links = blocks.StreamBlock([
        ("mega_menu_links", LinkWithURLANDSubLinks()),
    ],
        required=False,
        blank=True,
        max_num=5,
        min_num=0,
    )
    richtext_and_images = blocks.StreamBlock([
        ("advanced_rich_text", AdvancedRichTextBlock()),
        (
            "image_with_links",
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
        max_num=1,
        min_num=0, )

    class Meta:
        template = ("patterns/molecules/navigation/blocks/megamenu_contents.html",)


class MegaMenu(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    sub_text = blocks.CharBlock(required=False)
    column_1 = blocks.StreamBlock([
        ("column_1_contents", MegaMenuContent()),
    ],
        required=False,
        blank=True,
        max_num=1,
        min_num=0,
    )
    column_2 = blocks.StreamBlock([
        ("column_2_contents", MegaMenuContent()),
    ],
        required=False,
        blank=True,
        max_num=1,
        min_num=0,
    )
    column_3 = blocks.StreamBlock([
        ("column_3_contents", MegaMenuContent()),
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


class NoticeBarLinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Subtitle", required=False, max_length=200,
                             help_text=_("200 characters max limit"))
    page = blocks.PageChooserBlock(required=False, help_text="The link selected or inputted "
                                                             "here will transform the subtitle"
                                                             " entered above into a hyperlink")
    url = blocks.URLBlock(required=False, help_text="The link selected or inputted "
                                                    "here will transform the subtitle"
                                                    " entered above into a hyperlink")

    def clean(self, value):
        errors = {}
        # Set only a Page OR a URL
        if value["url"] and value["page"]:
            message = "Please choose a page or set a URL."

            errors["page"] = ErrorList([message])
            errors["url"] = ErrorList([message])

        # A URL must have title
        if value["url"] and not value["title"]:
            errors["title"] = ErrorList(["Please set a title for the URL"])
        if value["page"] and not value["title"]:
            errors["title"] = ErrorList(["Please set a title for the Page"])

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)


class NoticeBarWithMessageLink(blocks.StructBlock):
    title = blocks.CharBlock(
        required=False,
        max_length=75,
        help_text=_("75 characters max limit"),
    )
    subtitle = blocks.StreamBlock([
        ("subtitle", NoticeBarLinkBlock()),
    ],
        required=False,
        blank=True,
        max_num=1,
        min_num=0,
    )
    button = blocks.StreamBlock(
        [
            ("button", SecondaryCallToAction())
        ],
        blank=True,
        max_num=1,
        min_num=0,
        required=False,
    )

    enable = blocks.BooleanBlock(
        required=False,
        default=False,
    )

    class Meta:
        template = ("patterns/molecules/notice-bar/blocks/notice_bar.html",)

# -*- coding: utf-8 -*-
import re

from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock
from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock


class StoryLinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title", required=False
    )
    summary = blocks.CharBlock(required=False)

    class Meta:
        template = ("TODO",)


class StoryBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(required=False)
    summary = blocks.CharBlock(required=False)
    links = blocks.StreamBlock(
        [
            ('link', StoryLinkBlock()),
        ],
        max_num=3,
        min_num=0,
        required=False,
    )

    class Meta:
        template = ("TODO",)


class PinnedStoryBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(required=False)
    summary = blocks.CharBlock(required=False)

    class Meta:
        template = ("TODO",)


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)

    class Meta:
        icon = "image"
        template = "patterns/molecules/streamfield/blocks/image_block.html"


class DocumentBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    title = blocks.CharBlock(required=False)

    class Meta:
        icon = "doc-full-inverse"
        template = "patterns/molecules/streamfield/blocks/document_block.html"


class AlertBlock(blocks.PageChooserBlock):
    class Meta:
        label = "AlertBlock"
        template = "TODO"

    pass


class ContactDetailBlock(blocks.PageChooserBlock):
    class Meta:
        label = "ContactDetailBlock"
        template = "TODO"

    pass


class JumpboxWithImageBlock(blocks.StructBlock):
    class Meta:
        label = "JumpboxWithImageBlock"
        template = "TODO"

    image = ImageChooserBlock()
    page = blocks.PageChooserBlock(required=False)
    description = blocks.CharBlock(required=False)
    text = blocks.CharBlock(required=False)
    url = blocks.URLBlock(required=False)


class JumpboxBlock(blocks.StructBlock):
    class Meta:
        label = "JumpboxBlock"
        template = "TODO"

    page = blocks.PageChooserBlock(required=False)
    description = blocks.CharBlock(required=False)
    text = blocks.CharBlock(required=False)
    url = blocks.URLBlock(required=False)


class PersonBlock(blocks.PageChooserBlock):
    class Meta:
        label = "PersonBlock"
        template = "TODO"

    pass


class PlaceBlock(blocks.PageChooserBlock):
    class Meta:
        label = "PlaceBlock"
        template = "TODO"

    pass


class RichTextBlock(blocks.RichTextBlock):
    class Meta:
        label = "RichTextBlock"
        template = "TODO"

    pass


class RoleBlock(blocks.PageChooserBlock):
    class Meta:
        label = "RoleBlock"
        template = "TODO"

    pass


class TableBlock(WagtailTableBlock):
    class Meta:
        label = "TableBlock"
        template = "TODO"

    pass


class YoutubeLinkValue(blocks.StructValue):
    def embedding_url(self):

        url = self.get("url", None)
        if url is None:
            return None

        if "/embed/" in url:
            return url

        pattern = r"^(http(s)?:\/\/)?(www\.)?((youtu)(be)?)?"
        pattern += r"(\.(com)|\.(be))?(\/)(watch\?v=)?|(\&.+)?"

        video_id = re.sub(pattern, "", url)
        video_id = re.sub(r"(&list.+)|((\s)$)", "", video_id)

        return f"https://www.youtube.com/embed/{video_id}"


class YoutubeVideoBlock(blocks.StructBlock):
    class Meta:
        label = "YoutubeVideoBlock"
        value_class = YoutubeLinkValue

    url = blocks.CharBlock()


class BaseSectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    body = blocks.StreamBlock([], required=False)

# -*- coding: utf-8 -*-
import re

from django.forms.utils import ErrorList
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock
from wagtail.core import blocks
from wagtail.core.blocks.struct_block import StructBlockValidationError
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import VideoChooserBlock

from irelandie_utils.constants import StoryAlignment, StoryBackground


class StoryLinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title", required=False
    )
    summary = blocks.CharBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )

    class Meta:
        template = "patterns/molecules/streamfield/blocks/story_link_block.html"

    def clean(self, value):
        errors = {}
        values = [value["page"], value["url"]]
        # Set only a Page OR a URL
        if sum(value is not None and value != "" for value in values) != 1:
            message = "Please choose only a page or set a URL."

            errors["page"] = ErrorList([message])
            errors["url"] = ErrorList([message])

        # A URL must have title
        if value["url"] and not value["title"]:
            errors["title"] = ErrorList(["Please set a title for the URL"])

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)

        # user input data
        block_page = ctx["value"]["page"]
        block_url = ctx["value"]["url"]
        block_title = ctx["value"]["title"]

        # based on the input data, determine the intended link title & URL
        link_title = ""
        link_url = ""

        if block_page:
            link_title = block_title or block_page.title
            link_url = block_page.url

        if block_url:
            link_title = block_title
            link_url = block_url

        # added link_title,link_url in the context for FE to use them
        ctx.update({"link_title": link_title, "link_url": link_url})

        return ctx


class StoryBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(required=False)
    summary = blocks.CharBlock(required=False)
    alignment = blocks.ChoiceBlock(
        required=True,
        choices=StoryAlignment.choices,
    )
    background = blocks.ChoiceBlock(
        required=True,
        choices=StoryBackground.choices
    )
    links = blocks.StreamBlock(
        [
            ("link", StoryLinkBlock()),
        ],
        max_num=3,
        min_num=0,
        required=False,
    )

    class Meta:
        template = "patterns/molecules/streamfield/blocks/story_block.html"


class FeaturedStoryBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(required=False)

    class Meta:
        template = "patterns/molecules/streamfield/blocks/featured_story_block.html"

class EmbassyStory(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    page = blocks.PageChooserBlock(
        required=False,
        page_type="irelandie_missions.MissionPage",
    )
    title = blocks.CharBlock(required=False)

    class Meta:
        template = "patterns/molecules/streamfield/blocks/embassy_block.html"


class PinnedStoryBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(required=False)
    summary = blocks.CharBlock(required=False)

    class Meta:
        template = "patterns/molecules/streamfield/blocks/pinned_story_block.html"


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


class SocialLinkBlock(blocks.StructBlock):
    class Meta:
        label = "Social Link"
        template = "patterns/molecules/streamfield/blocks/social_link_block.html"

    url = blocks.URLBlock(required=False)


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
        label = "Youtube Video"
        value_class = YoutubeLinkValue
        template = "patterns/molecules/streamfield/blocks/youtube_block.html"

    url = blocks.CharBlock()


class CustomVideoChooserBlock(VideoChooserBlock):
    pass


class BaseSectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    body = blocks.StreamBlock([], required=False)


class ArticleStoryBlock(blocks.StreamBlock):
    contact_detail = ContactDetailBlock()
    image = ImageBlock()
    rich_text = blocks.RichTextBlock(features=["h3", "blockquote", "bold", "link", "document-link", "ul"])
    person = PersonBlock()
    place = PlaceBlock()
    document = DocumentBlock()
    table = TableBlock()
    role = RoleBlock()
    video = CustomVideoChooserBlock()
    youtube_video = YoutubeVideoBlock()

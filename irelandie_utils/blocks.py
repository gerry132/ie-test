# -*- coding: utf-8 -*-

import re

from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock
from wagtail.core import blocks
from wagtail.core.blocks.struct_block import StructBlockValidationError, StructValue
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import VideoChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from irelandie_utils.constants import StoryAlignment, StoryBackground


ALT_HELP_TEXT = """A short one-sentence literal description
                    of the %s is
                    required to make the page accessible to the
                    visually impaired. Details: https://axesslab.com/alt-texts/"""


ALT_VID = ALT_HELP_TEXT % 'video'
ALT_IMAGE = ALT_HELP_TEXT % 'image'


class BaseBlockLinkValidation(blocks.StructBlock):
    def clean(self, value):
        errors = {}
        values = [value["page"], value["url"]]
        # Set only a Page OR a URL or both can be blank
        if all(values):
            message = "Please choose only a page or set a URL."

            errors["page"] = ErrorList([message])
            errors["url"] = ErrorList([message])

        # A URL must have title
        if value["url"] and not value["title"]:
            errors["title"] = ErrorList(["Please set a title for the URL"])

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)


class BaseBlockLinkContext(blocks.StructBlock):
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        try:
            # A block may not have a page or url field
            if value["url"]:
                context["link_url"] = value["url"]
            elif value["page"]:
                context["link_url"] = value["page"].url

        except KeyError:
            context["link_url"] = None

        try:
            if value["title"]:
                context["link_title"] = value["title"]
            else:
                if value["page"]:
                    context["link_title"] = value["page"].title
                elif value["url"]:
                    context["link_title"] = value["title"]

        except KeyError:
            context["link_title"] = None

        return context


class StoryLinkBlock(BaseBlockLinkValidation, BaseBlockLinkContext):
    page = blocks.PageChooserBlock(required=False)
    icon = blocks.ChoiceBlock(
        choices=(
            ("", "Choose an icon (optional)"),
            ("government-building", "Government Building"),
            ("money", "Money"),
            ("passport", "Passport"),
            ("plane", "Plane"),
            ("ticket", "Ticket"),
        ),
        required=False,
    )
    image = ImageChooserBlock(required=False)
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


class StoryBlock(BaseBlockLinkValidation, BaseBlockLinkContext):
    image = ImageChooserBlock(required=True)
    image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )
    primary_title = blocks.CharBlock(required=False, label="Supporting title")
    title = blocks.CharBlock(required=False)
    summary = blocks.RichTextBlock(
        features=["h3", "blockquote", "bold", "link", "document-link", "ul"],
        required=False,
    )
    alignment = blocks.ChoiceBlock(
        required=True,
        choices=StoryAlignment.choices,
        default=StoryAlignment.LEFT,
    )
    background = blocks.ChoiceBlock(
        required=True,
        choices=StoryBackground.choices,
        default=StoryBackground.LIGHT,
    )
    links = blocks.StreamBlock(
        [
            ("link", StoryLinkBlock()),
        ],
        max_num=6,
        min_num=0,
        required=False,
    )

    class Meta:
        icon = "snippet"
        template = "patterns/molecules/streamfield/blocks/story_block.html"


class TopStoryBlock(BaseBlockLinkValidation, BaseBlockLinkContext):
    image = ImageChooserBlock(required=True)
    image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )
    primary_title = blocks.CharBlock(required=False, label="Supporting title")
    title = blocks.CharBlock(required=False)
    summary = blocks.CharBlock(required=False)
    alignment = blocks.ChoiceBlock(
        required=True,
        choices=StoryAlignment.choices,
        default=StoryAlignment.LEFT,
    )
    background = blocks.ChoiceBlock(
        required=True,
        choices=StoryBackground.choices,
        default=StoryBackground.LIGHT,
    )
    link_text = blocks.CharBlock()

    class Meta:
        icon = "snippet"
        template = "patterns/molecules/streamfield/blocks/top_story_block.html"


class FeaturedStoryBlock(BaseBlockLinkValidation, BaseBlockLinkContext):
    image = ImageChooserBlock(required=True)
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )
    primary_title = blocks.CharBlock(required=False, label="Supporting title")
    title = blocks.CharBlock(required=False)

    class Meta:
        icon = "doc-full-inverse"
        template = "patterns/molecules/streamfield/blocks/featured_story_block.html"


class EmbassyStory(BaseBlockLinkValidation, BaseBlockLinkContext):
    image = ImageChooserBlock(required=True)
    page = blocks.PageChooserBlock(
        required=False,
        page_type="irelandie_missions.MissionPage",
    )
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )
    primary_title = blocks.CharBlock(required=False, label="Supporting title")
    title = blocks.CharBlock(required=False)

    class Meta:
        icon = "doc-full"
        template = "patterns/molecules/streamfield/blocks/embassy_block.html"


class AlernatePinnedStoryHeroLinkText(StructValue):
    def link_text(self):
        text = self.get("button_text") or self.get("page")
        return text


class PinnedStoryHeroBlock(BaseBlockLinkValidation):
    image = ImageChooserBlock(required=True)
    image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
    title = blocks.CharBlock(required=False)
    summary = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )
    button_text = blocks.CharBlock(required=False)

    class Meta:
        value_class = AlernatePinnedStoryHeroLinkText
        template = "patterns/molecules/streamfield/blocks/pinned_story_hero_block.html"


class PinnedStoryBlock(BaseBlockLinkValidation):
    image = ImageChooserBlock(required=True)
    image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )
    title = blocks.CharBlock(required=False)
    summary = blocks.CharBlock(required=False)

    class Meta:
        template = "patterns/molecules/streamfield/blocks/pinned_story_block.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
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
        template = "patterns/molecules/streamfield/blocks/alert_block.html"

    pass


class ContactDetailBlock(blocks.PageChooserBlock):
    class Meta:
        label = "ContactDetailBlock"
        template = "patterns/molecules/streamfield/blocks/contact_block.html"

    pass


class JumpboxWithImageBlock(blocks.StructBlock):
    class Meta:
        label = "JumpboxWithImageBlock"
        template = "TODO"

    image = ImageChooserBlock()
    # TODO: add image_alt
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


class PersonBlock(blocks.StructBlock):
    person = SnippetChooserBlock(target_model="irelandie_people.Person")

    class Meta:
        icon = "user"
        label = "Person"
        template = "patterns/molecules/streamfield/blocks/person_block.html"


class PlaceBlock(blocks.PageChooserBlock):
    class Meta:
        label = "PlaceBlock"
        template = "patterns/molecules/streamfield/blocks/place_block.html"

    pass


class RichTextBlock(blocks.RichTextBlock):

    class Meta:
        label = "RichTextBlock"
        template = "patterns/molecules/streamfield/blocks/paragraph_block.html"


class RoleBlock(blocks.PageChooserBlock):
    class Meta:
        label = "RoleBlock"
        template = "patterns/molecules/streamfield/blocks/role_block.html"

    pass


class TableBlock(WagtailTableBlock):
    class Meta:
        label = "TableBlock"


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
        icon = "media"
        label = "Youtube Video"
        value_class = YoutubeLinkValue
        template = "patterns/molecules/streamfield/blocks/youtube_block.html"

    url = blocks.CharBlock()
    slido_embed = blocks.TextBlock(
        required=False,
        help_text=_(
            "Slido iframe code. Ensure that the code you add here is only Slido provided code."
        ),
    )


class CustomVideoChooserBlock(VideoChooserBlock):
    video_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_VID),
    )

    class Meta:
        icon = "media"
        label = "Custom Video Chooser"
        template = "patterns/molecules/streamfield/blocks/video_block_alt.html"


class CustomVideoChooserBlockAlt(blocks.StructBlock):
    video = CustomVideoChooserBlock()
    video_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_VID),
    )

    class Meta:
        icon = "media"
        label = "Custom Video Chooser"
        template = "patterns/molecules/streamfield/blocks/video_block.html"


class BaseSectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    body = blocks.StreamBlock([], required=False)


class LogoCardBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
    title = blocks.CharBlock()
    summary = blocks.TextBlock()
    url = blocks.URLBlock()

    class Meta:
        icon = "image"
        label = "Logo Card"
        template = "patterns/molecules/logo_card/logo_card.html"


class LogoCardsBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    summary = blocks.TextBlock()
    cards = blocks.StreamBlock([("card", LogoCardBlock())])

    class Meta:
        icon = "pick"
        label = "Logo Cards"
        template = "patterns/molecules/streamfield/blocks/logo_cards.html"


class ArticleCardBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
    title = blocks.CharBlock()
    summary = blocks.TextBlock()
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )

    class Meta:
        icon = "image"
        label = "Article Card"
        template = "patterns/molecules/article_card/article_card.html"

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
        context = super().get_context(value, parent_context=parent_context)
        context["link_url"] = value["url"] or value["page"].url
        return context


class ArticleCardsBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    summary = blocks.TextBlock()
    articles = blocks.StreamBlock([("article", ArticleCardBlock())])

    class Meta:
        icon = "list-ul"
        label = "Articles"
        template = "patterns/molecules/streamfield/blocks/article_cards.html"


class FeaturedArticlesBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    summary = blocks.TextBlock()
    articles = blocks.ListBlock(
        blocks.PageChooserBlock(
            page_type=[
                "irelandie_corporate_information.CorportateInformationPage",
                "irelandie_news.NewsPage",
                "irelandie_press_releases.PressReleasePage",
                "irelandie_publications.PublicationPage",
                "irelandie_speeches.SpeechPage",
                "irelandie_site_information.SiteInformationPage",
            ]
        ),
        min_num=3,
        max_num=3,
    )

    class Meta:
        icon = "list-ol"
        label = "Featured Articles"
        template = "patterns/molecules/streamfield/blocks/featured_articles.html"


class ArticleStoryBlock(blocks.StreamBlock):
    rich_text = RichTextBlock(group="Base")
    image = ImageBlock(group="Base")
    document = DocumentBlock(group="Base")

    person = PersonBlock(group="Module")

    html = blocks.RawHTMLBlock(
        group="HTML",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
    )
    role = RoleBlock(group="HTML")
    table = TableBlock(group="HTML")
    video = CustomVideoChooserBlockAlt(group="HTML")
    youtube_video = YoutubeVideoBlock(group="HTML")


class PinnedStoriesBlock(blocks.StructBlock):
    pinned_story_hero = PinnedStoryHeroBlock()
    pinned_stories = blocks.ListBlock(PinnedStoryBlock())

    class Meta:
        icon = "thumbtack"
        label = "Pinned Stories"
        template = "patterns/molecules/pinned-stories/pinned_stories.html"


class MapBlock(blocks.StructBlock):
    iframe = blocks.RawHTMLBlock(required=False)
    width = blocks.IntegerBlock(max_num=100, required=False)


class AccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    summary = blocks.RichTextBlock(
        features=["h3", "blockquote", "bold", "link", "document-link", "ul"],
        required=False,
    )
    accordions = blocks.StreamBlock(
        [
            (
                "accordion",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock()),
                        (
                            "content",
                            blocks.RichTextBlock(
                                features=[
                                    "h1",
                                    "h2",
                                    "h3",
                                    "h4",
                                    "h5",
                                    "h6",
                                    "blockquote",
                                    "bold",
                                    "link",
                                    "document-link",
                                    "ul",
                                    "image",
                                ]
                            ),
                        ),
                        ("additional", blocks.StreamBlock([
                            ("map", MapBlock()),
                            ("table", TableBlock(group="table")),
                            ("document", DocumentBlock(required=False)),
                            ("youtube", YoutubeVideoBlock(group="HTML")),
                        ], required=False)
                         ),
                    ]
                ),
            )
        ]
    )
    background = blocks.ChoiceBlock(
        required=True,
        choices=StoryBackground.choices,
        default=StoryBackground.LIGHT,
    )

    class Meta:
        icon = "collapse-down"
        label = "Accordion"
        template = "patterns/molecules/accordion/accordion.html"


class FreeFormBlocksBase(blocks.StreamBlock):
    pinned_stories = PinnedStoriesBlock(group="Module")
    stories = StoryBlock(group="Module")

    video = CustomVideoChooserBlockAlt(group="HTML")
    youtube_video = YoutubeVideoBlock(group="HTML")

    person = PersonBlock(group="Snippets")


class FreeFormBlocks(FreeFormBlocksBase):
    rich_text = RichTextBlock(group="Base")
    image = ImageBlock(group="Base")
    document = DocumentBlock(group="Base")
    accordion = AccordionBlock(group="Base")

    articles = ArticleCardsBlock(group="Module")
    embassy_story = EmbassyStory(group="Module")
    featured_articles = FeaturedArticlesBlock(group="Module")
    featured_story = FeaturedStoryBlock(group="Module")
    logos = LogoCardsBlock(group="Module")

    table = TableBlock(group="HTML")
    html = blocks.RawHTMLBlock(
        group="HTML",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
    )

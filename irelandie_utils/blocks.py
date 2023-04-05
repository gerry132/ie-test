# -*- coding: utf-8 -*-

import re

from django.forms.utils import ErrorList
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError, StructValue
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import VideoChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from irelandie_home.blocks import SecondaryCallToAction

from irelandie_utils.constants import StoryAlignment, StoryBackground, ParagraphAlignment

ALT_HELP_TEXT = """A short one-sentence literal description
                    of the %s is
                    required to make the page accessible to the
                    visually impaired. Details: https://axesslab.com/alt-texts/"""

ALT_VID = ALT_HELP_TEXT % 'video'
ALT_IMAGE = ALT_HELP_TEXT % 'image'
ALT_ICON = ALT_HELP_TEXT % 'icon'


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
            ("authentication", "Authentication"),
            ("citizenship", "Citizenship"),
            ("closure-dates", "Closure Dates"),
            ("consular-fees", "Consular Fees"),
            ("contact-phone", "Contact Phone"),
            ("contact-mail", "Contact Mail"),
            ("family", "Family"),
            ("government-building", "Government Building"),
            ("how-we-can-help", "How We Can Help"),
            ("information", "Information"),
            ("invest", "Invest"),
            ("jobs", "Jobs"),
            ("link", "Link"),
            ("live", "Live"),
            ("location", "Location"),
            ("marriage", "Marriage"),
            ("money", "Money"),
            ("new-to", "New To"),
            ("news", "News"),
            ("notice", "Notice"),
            ("opening-hours", "Opening Hours"),
            ("passport", "Passport"),
            ("plane", "Plane"),
            ("services", "Services"),
            ("study", "Study"),
            ("ticket", "Ticket"),
            ("trade", "Trade"),
            ("trade2", "Trade2"),
            ("travel", "Travel"),
            ("visas", "Visas"),
            ("working-holiday", "Working Holiday"),
        ),
        required=False,
    )
    image = ImageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title", required=False
    )
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )

    def clean(self, value):
        errors = {}
        values = [value["page"], value["url"]]
        # Set only a Page OR a URL
        if sum(value is not None and value != "" for value in values) != 1:
            message = "Please choose a page or set a URL."

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
        try:
            # A block may not have a page or url field
            if value["url"]:
                context["link_url"] = value["url"]
            elif value["page"]:
                context["link_url"] = value["page"].url

        except KeyError:
            context["link_url"] = None
        return context

    class Meta:
        template = "patterns/molecules/streamfield/blocks/story_link_block.html"


class StoryBlock(BaseBlockLinkValidation, BaseBlockLinkContext):
    image = ImageChooserBlock(required=False)
    image_alt = blocks.CharBlock(
        required=False,
        help_text=_(ALT_IMAGE),
    )
    image_credit = blocks.CharBlock(required=False, max_length=255)
    video = VideoChooserBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )
    primary_title = blocks.CharBlock(required=False, label="Supporting title")
    title = blocks.CharBlock(required=False)
    summary = blocks.RichTextBlock(
        features=["h3", "blockquote", "bold", "link", "document-link", "ul", "ol"],
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
    button_link = blocks.StreamBlock(
        [
            ("button", SecondaryCallToAction())
        ],
        blank=True,
        max_num=1,
        min_num=0,
        required=False,
    )
    links = blocks.StreamBlock(
        [
            ("link", StoryLinkBlock()),
        ],
        max_num=6,
        min_num=0,
        required=False,
    )

    def clean(self, value):
        errors = {}
        person_image = value.get('image')
        video = value.get('video')

        if not (bool(person_image) ^ bool(video)):
            msg = "You can't choose both an image and a video. Choose an image or a video"
            errors['image'] = ErrorList([msg])
            errors['video'] = ErrorList([msg])

        if not (bool(person_image) | bool(video)):
            msg = "You have to choose either an image or a video."
            errors['image'] = ErrorList([msg])
            errors['video'] = ErrorList([msg])

        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)

    class Meta:
        icon = "snippet"
        label = "Two Column Feature"
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
        text = self.get("title") or self.get("page")
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
    image_credit = blocks.CharBlock(required=False, max_length=255)
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


class AdvancedRichTextBlock(blocks.StructBlock):
    section_id = blocks.CharBlock(required=False)
    paragraph_alignment = blocks.ChoiceBlock(
        required=False,
        choices=ParagraphAlignment.choices,
        default=ParagraphAlignment.WIDE,
    )
    heading = blocks.CharBlock(required=False)
    rich_text = blocks.RichTextBlock(
        features=["h3", "blockquote", "bold", "link", "document-link", "ul", "ol"], required=False,
    )
    button_link = blocks.StreamBlock(
        [
            ("button", SecondaryCallToAction())
        ],
        blank=True,
        max_num=1,
        min_num=0,
        required=False,
    )

    class Meta:
        label = "Advanced RichTextBlock"
        template = "patterns/molecules/streamfield/blocks/advanced_richtext_block.html"


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
    url = blocks.URLBlock(required=False)

    class Meta:
        icon = "image"
        label = "Logo Card"
        template = "patterns/molecules/logo_card/logo_card.html"


class LogoCardsBlock(blocks.StructBlock):
    summary_richtext = blocks.StructBlock(
        [
            ("content", AdvancedRichTextBlock())
        ],
        blank=True,
        null=True,
    )
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
    link_text = blocks.CharBlock(
        max_length=32, blank=True, required=False, default="Read Story", help_text='Call To Action Text'
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
        try:
            # A block may not have a page or url field
            if value["url"]:
                context["link_url"] = value["url"]
            elif value["page"]:
                context["link_url"] = value["page"].url

        except KeyError:
            context["link_url"] = None
        return context


class ArticleCardsBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    summary = blocks.TextBlock(required=False)
    summary_richtext = AdvancedRichTextBlock(required=False)

    articles = blocks.StreamBlock([("article", ArticleCardBlock())])

    class Meta:
        icon = "list-ul"
        label = "Articles"
        template = "patterns/molecules/streamfield/blocks/article_cards.html"


class StatBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    summary = blocks.RichTextBlock(
        features=["h3", "blockquote", "bold", "link", "document-link", "ul", "ol"],
        required=False,
    )

    class Meta:
        icon = "list-ul"
        label = "Stat Block"
        template = "patterns/molecules/streamfield/blocks/stat_block.html"


class StatsBlock(blocks.StructBlock):
    richtext = AdvancedRichTextBlock(required=False)

    stats = blocks.StreamBlock([("stats", StatBlock())])

    class Meta:
        icon = "list-ul"
        label = "Stats Block"
        template = "patterns/molecules/streamfield/blocks/stats_block.html"


class LinkCardBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
    title = blocks.CharBlock()
    summary = blocks.TextBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )

    class Meta:
        icon = "image"
        label = "Link Card"
        template = "patterns/molecules/link_card/link_card.html"

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
        try:
            # A block may not have a page or url field
            if value["url"]:
                context["link_url"] = value["url"]
            elif value["page"]:
                context["link_url"] = value["page"].url

        except KeyError:
            context["link_url"] = None
        return context


class LinkCardsBlock(blocks.StructBlock):
    link_cards = blocks.StreamBlock([("link_card", LinkCardBlock())])

    class Meta:
        icon = "list-ul"
        label = "Link Cards"
        template = "patterns/molecules/streamfield/blocks/link_cards.html"


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


class ContactBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=255, required=False)
    address_line_1 = blocks.CharBlock(max_length=255, blank=True, null=True, required=False)
    address_line_2 = blocks.CharBlock(max_length=255, blank=True, null=True, required=False)
    address_line_3 = blocks.CharBlock(max_length=255, blank=True, null=True, required=False)
    address_line_4 = blocks.CharBlock(max_length=255, blank=True, null=True, required=False)
    post_code = blocks.CharBlock(max_length=25, null=True, blank=True, required=False)
    map_link = blocks.CharBlock(blank=True, help_text="Hyperlink to google maps", required=False)
    international_code = blocks.CharBlock(max_length=5,
                                          blank=True,
                                          validators=[
                                              RegexValidator(
                                                  regex=r'^\+\d+$',
                                                  message="Examples: +353 +01",
                                                  code='invalid'
                                              )
                                          ],
                                          help_text="Format must be +123",
                                          required=False
                                          )
    telephone = blocks.CharBlock(max_length=30, blank=True, required=False)
    alt_international_code = blocks.CharBlock(max_length=5,
                                              blank=True,
                                              validators=[
                                                  RegexValidator(
                                                      regex=r'^\+\d+$',
                                                      message="Examples: +353 +01",
                                                      code='invalid'
                                                  )
                                              ],
                                              help_text="Format must be +123",
                                              required=False
                                              )
    alt_telephone = blocks.CharBlock(max_length=30, blank=True, required=False)
    fax_number = blocks.CharBlock(max_length=50, blank=True, required=False)
    email = blocks.RichTextBlock(blank=True, required=False)


class StoryPhotoGalleryBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
    heading = blocks.CharBlock(required=False)
    rich_text_summary = blocks.RichTextBlock(required=False)
    button_link = blocks.StreamBlock(
        [
            ("button", SecondaryCallToAction())
        ],
        blank=True,
        max_num=1,
        min_num=0,
        required=False,
    )

    class Meta:
        label = "Story Photo Gallery"


class StoryPhotoGalleriesBlock(blocks.StructBlock):
    richtext = AdvancedRichTextBlock(required=False)
    story_photo_gallery = blocks.StreamBlock([("story_photo_gallery", StoryPhotoGalleryBlock())])

    class Meta:
        icon = "list-ul"
        label = "Story Photo Gallery"
        template = "patterns/molecules/streamfield/blocks/story_photo_galleries_block.html"


class ArticleStoryBlock(blocks.StreamBlock):
    rich_text = RichTextBlock(group="Base")
    rich_text_advanced = AdvancedRichTextBlock(group="Base")
    image = ImageBlock(group="Base")
    document = DocumentBlock(group="Base")

    person = PersonBlock(group="Module")
    logos = LogoCardsBlock(group="Module")

    html = blocks.RawHTMLBlock(
        group="HTML",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
    )
    role = RoleBlock(group="HTML")
    table = TableBlock(table_options={'renderer': 'html'}, group="HTML")
    video = CustomVideoChooserBlockAlt(group="HTML")
    youtube_video = YoutubeVideoBlock(group="HTML")


class MinimalArticleStoryBlock(blocks.StreamBlock):
    rich_text = RichTextBlock(group="Base")
    rich_text_advanced = AdvancedRichTextBlock(group="Base")
    image = ImageBlock(group="Base")
    document = DocumentBlock(group="Base")

    logos = LogoCardsBlock(group="Module")
    table = TableBlock(table_options={'renderer': 'html'}, group="Module")
    youtube_video = YoutubeVideoBlock(group="Module")
    story_photo_gallery = StoryPhotoGalleriesBlock(group="Base")


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
    summary_richtext = AdvancedRichTextBlock(required=False)
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
                                ], required=False,
                            ),
                        ),
                        ("button_link", blocks.StreamBlock(
                            [
                                ("button", SecondaryCallToAction())
                            ],
                            blank=True,
                            max_num=1,
                            min_num=0,
                            required=False, )
                         ),
                        ("additional", blocks.StreamBlock([
                            ("map", MapBlock()),
                            ("table", TableBlock(table_options={'renderer': 'html'}, group="table")),
                            ("document", DocumentBlock(required=False)),
                            ("youtube", YoutubeVideoBlock(group="HTML")),
                            ("contact_details",
                             SnippetChooserBlock(target_model="utils.ContactSnippet"))
                        ], required=False)
                         ),
                    ]
                ),
            )
        ]
    )

    class Meta:
        icon = "collapse-down"
        label = "Accordion"
        template = "patterns/molecules/accordion/accordion.html"


class FreeFormBlocksBase(blocks.StreamBlock):
    pinned_stories = blocks.StructBlock(
        [
            ("pinned_story_hero", PinnedStoryHeroBlock()),
        ],
        template="patterns/molecules/pinned-stories/pinned_stories.html", group="Module"
    )
    story_photo_gallery = StoryPhotoGalleriesBlock(group="Base")
    stories = StoryBlock(group="Module")

    video = CustomVideoChooserBlockAlt(group="HTML")
    youtube_video = YoutubeVideoBlock(group="HTML")

    person = PersonBlock(group="Snippets")


class RelatedContentBlock(BaseBlockLinkValidation, BaseBlockLinkContext):
    # icon = blocks.ChoiceBlock(
    #     choices=(
    #         ("", "Choose an icon (optional)"),
    #         ("authentication", "Authentication"),
    #         ("citizenship", "Citizenship"),
    #         ("closure-dates", "Closure Dates"),
    #         ("consular-fees", "Consular Fees"),
    #         ("contact-phone", "Contact Phone"),
    #         ("contact-mail", "Contact Mail"),
    #         ("family", "Family"),
    #         ("government-building", "Government Building"),
    #         ("how-we-can-help", "How We Can Help"),
    #         ("information", "Information"),
    #         ("invest", "Invest"),
    #         ("jobs", "Jobs"),
    #         ("link", "Link"),
    #         ("live", "Live"),
    #         ("location", "Location"),
    #         ("marriage", "Marriage"),
    #         ("money", "Money"),
    #         ("new-to", "New To"),
    #         ("news", "News"),
    #         ("notice", "Notice"),
    #         ("opening-hours", "Opening Hours"),
    #         ("passport", "Passport"),
    #         ("plane", "Plane"),
    #         ("services", "Services"),
    #         ("study", "Study"),
    #         ("ticket", "Ticket"),
    #         ("trade", "Trade"),
    #         ("trade2", "Trade2"),
    #         ("travel", "Travel"),
    #         ("visas", "Visas"),
    #         ("working-holiday", "Working Holiday"),
    #     ),
    #     required=False,
    # )
    # image = ImageChooserBlock(required=False)
    # image_alt = blocks.CharBlock(
    #     required=False,
    #     help_text=_(ALT_IMAGE),
    # )
    title = blocks.CharBlock()
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )

    class Meta:
        label = "Related Content"


class TocBlocks(blocks.StreamBlock):
    rich_text = AdvancedRichTextBlock(group="Base")
    document = DocumentBlock(group="Base")
    table = TableBlock(table_options={'renderer': 'html'}, group="HTML")


class GeneralContentBlocks(blocks.StreamBlock):
    rich_text = AdvancedRichTextBlock(group="Base")
    image = ImageBlock(group="Base")
    document = DocumentBlock(group="Base")
    html = blocks.RawHTMLBlock(
        group="HTML",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
    )
    table = TableBlock(table_options={'renderer': 'html'}, group="HTML")
    youtube_video = YoutubeVideoBlock(group="HTML")
    accordion = AccordionBlock(group="Base")
    logos = LogoCardsBlock(group="Base")
    stats_block = StatsBlock(group="Base")
    story_photo_gallery = StoryPhotoGalleriesBlock(group="Base")


class TocBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    content = TocBlocks(required=False)


class TocBlockSnippets(blocks.StreamBlock):
    visas = SnippetChooserBlock(target_model="utils.Visa")
    passports = SnippetChooserBlock(target_model="utils.Passport")
    authentication = SnippetChooserBlock(target_model="utils.Authentication")
    marriage = SnippetChooserBlock(target_model="utils.Marriage")
    contact_details = SnippetChooserBlock(target_model="utils.ContactSnippet")


class TocAdminBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    content = blocks.StreamBlock(
        [
            ("content", GeneralContentBlocks()),
            ("snippets", TocBlockSnippets())
        ],
        required=False,
    )


class AdditionalSocialBlock(blocks.StructBlock):
    social_logo = ImageChooserBlock(required=False)
    social_url = blocks.URLBlock(
        label="Social_URL",
        required=False,
        help_text="URL for logo click",
    )
    social_link_text = blocks.CharBlock(required=False)

    class Meta:
        label = "Additional Social Feed"
        template = "patterns/molecules/streamfield/blocks/additional_social_block.html"


class SocialFieldBlock(blocks.StructBlock):
    twitter_title = blocks.CharBlock(required=False)
    twitter_username = blocks.CharBlock(max_length=100, required=False, help_text="Twitter username")
    additional_social_feed = blocks.StreamBlock(
        [
            ("additional_social_feed", AdditionalSocialBlock())
        ],
        max_num=1,
        min_num=0,
        required=False,
    )


class PersonSocialBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=False)
    person_title = blocks.CharBlock(required=False)
    person_image = ImageChooserBlock(required=False)
    video = VideoChooserBlock(required=False)
    embassy_logo = ImageChooserBlock(required=False)
    person_social_feed = blocks.StreamBlock(
        [
            ("person_social_feed", AdditionalSocialBlock())
        ],
        max_num=1,
        min_num=0,
        required=False,
    )
    contact_details = SnippetChooserBlock(target_model="utils.ContactSnippet")
    opening_hours = blocks.RichTextBlock(required=False)
    closure_dates = blocks.RichTextBlock(required=False)
    emergency_contact_details = blocks.RichTextBlock(required=False)

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
    social_feed = blocks.StreamBlock(
        [
            ("social_feed", SocialFieldBlock()),
        ],
        max_num=1,
        min_num=0,
        required=False,
    )

    def clean(self, value):
        errors = {}
        person_image = value.get('person_image')
        video = value.get('video')

        if not (bool(person_image) ^ bool(video)):
            msg = "You can't choose both an image and a video. Choose an image or a video"
            errors['person_image'] = ErrorList([msg])
            errors['video'] = ErrorList([msg])

        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)

    class Meta:
        label = "Person + Social Feed"
        template = "patterns/molecules/streamfield/blocks/person_block.html"


class LinkBoxBlock(blocks.StructBlock):
    # icon = blocks.ChoiceBlock(
    #     choices=(
    #         ("", "Choose an icon (optional)"),
    #         ("authentication", "Authentication"),
    #         ("citizenship", "Citizenship"),
    #         ("closure-dates", "Closure Dates"),
    #         ("consular-fees", "Consular Fees"),
    #         ("contact-phone", "Contact Phone"),
    #         ("contact-mail", "Contact Mail"),
    #         ("family", "Family"),
    #         ("government-building", "Government Building"),
    #         ("how-we-can-help", "How We Can Help"),
    #         ("information", "Information"),
    #         ("invest", "Invest"),
    #         ("jobs", "Jobs"),
    #         ("link", "Link"),
    #         ("live", "Live"),
    #         ("location", "Location"),
    #         ("marriage", "Marriage"),
    #         ("money", "Money"),
    #         ("new-to", "New To"),
    #         ("news", "News"),
    #         ("notice", "Notice"),
    #         ("opening-hours", "Opening Hours"),
    #         ("passport", "Passport"),
    #         ("plane", "Plane"),
    #         ("services", "Services"),
    #         ("study", "Study"),
    #         ("ticket", "Ticket"),
    #         ("trade", "Trade"),
    #         ("trade2", "Trade2"),
    #         ("travel", "Travel"),
    #         ("visas", "Visas"),
    #         ("working-holiday", "Working Holiday"),
    #     ),
    #     required=False,
    # )
    # image = ImageChooserBlock(required=False)
    # image_alt = blocks.CharBlock(
    #     required=False,
    #     help_text=_(ALT_IMAGE),
    # )
    heading = blocks.CharBlock()
    introduction = blocks.RichTextBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )

    class Meta:
        icon = "image"
        label = "Link Box"
        template = "patterns/molecules/link_box/link_box.html"

    def clean(self, value):
        errors = {}
        values = [value["page"], value["url"]]
        # Set only a Page OR a URL
        if sum(value is not None and value != "" for value in values) != 1:
            message = "Please choose only a page or set a URL."

            errors["page"] = ErrorList([message])
            errors["url"] = ErrorList([message])

        # A URL must have title
        if value["url"] and not value["heading"]:
            errors["heading"] = ErrorList(["Please set a title for the URL"])

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)

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
        return context


class LinkBoxesBlock(blocks.StructBlock):
    link_boxes = blocks.StreamBlock([("link_box", LinkBoxBlock())])

    class Meta:
        icon = "list-ul"
        label = "Link Boxes"
        template = "patterns/molecules/streamfield/blocks/link_boxes.html"


class LinkButtonBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=25)
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(
        label="URL",
        required=False,
        help_text="An external link.",
    )

    class Meta:
        icon = "image"
        label = "Link Button"
        template = "patterns/molecules/link_button/link_button.html"

    def clean(self, value):
        errors = {}
        values = [value["page"], value["url"]]
        # Set only a Page OR a URL
        if sum(value is not None and value != "" for value in values) != 1:
            message = "Please choose only a page or set a URL."

            errors["page"] = ErrorList([message])
            errors["url"] = ErrorList([message])

        # A URL must have title
        if value["url"] and not value["heading"]:
            errors["heading"] = ErrorList(["Please set a title for the URL"])

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)

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
        return context


class GenericHeroBlock(blocks.StructBlock):
    hero_image_alignment = blocks.ChoiceBlock(
        required=True,
        choices=StoryAlignment.choices,
        default=StoryAlignment.RIGHT,
    )
    hero_image = ImageChooserBlock(required=False)
    hero_image_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_IMAGE),
    )
    hero_image_credit = blocks.CharBlock(required=False, max_length=255)
    hero_video = VideoChooserBlock(required=False)
    background_color = blocks.CharBlock(required=False, default='#E7E5E1')
    hero_title = blocks.CharBlock(required=True, max_length=120)
    subtitle = blocks.CharBlock(required=False)

    def clean(self, value):
        errors = {}
        hero_image = value.get('hero_image')
        hero_video = value.get('hero_video')

        if not (bool(hero_image) ^ bool(hero_video)):
            msg = "You should choose an image or a video."
            errors['hero_image'] = ErrorList([msg])
            errors['hero_video'] = ErrorList([msg])

        if bool(hero_image) and bool(hero_video):
            msg = "You can't choose both an image and a video. Choose an image or a video"
            errors['hero_image'] = ErrorList([msg])
            errors['hero_video'] = ErrorList([msg])

        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)

    class Meta:
        label = "Mini Hero Block"
        template = "patterns/molecules/streamfield/blocks/generic_hero.html"


class YoutubeVimeoLinkValue(blocks.StructValue):
    def embedding_url(self):

        url = self.get("youtube_or_vimeo_embed", None)
        if url is None:
            return None
        if "/embed/" in url:
            return url
        if 'youtube.com' in url or 'youtu.be' in url:
            pattern = r"^(http(s)?:\/\/)?(www\.)?((youtu)(be)?)?"
            pattern += r"(\.(com)|\.(be))?(\/)(watch\?v=)?|(\&.+)?"

            video_id = re.sub(pattern, "", url)
            video_id = re.sub(r"(&list.+)|((\s)$)", "", video_id)

            return f"https://www.youtube.com/embed/{video_id}"
        if 'vimeo.com' in url:
            embed_url = url.replace('vimeo.com', 'player.vimeo.com/video')
            embed_url_with_parameters = embed_url + '?controls=0'
            return embed_url_with_parameters
        else:
            return None


class VideoBlock(blocks.StructBlock):
    youtube_or_vimeo_embed = blocks.CharBlock(required=False)
    video = CustomVideoChooserBlock(required=False)
    video_alt = blocks.CharBlock(
        required=True,
        help_text=_(ALT_VID),
    )
    title = blocks.CharBlock()
    summary = blocks.TextBlock(required=False)

    def clean(self, value):
        errors = {}
        values = [value["youtube_or_vimeo_embed"], value["video"]]
        # Set only a Page OR a URL
        if sum(value is not None and value != "" for value in values) != 1:
            message = "Please choose only a youtube_or_vimeo_embed or set a custom_video."

            errors["youtube_or_vimeo_embed"] = ErrorList([message])
            errors["video"] = ErrorList([message])

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)

    class Meta:
        value_class = YoutubeVimeoLinkValue


class MultimediaRowBlock(blocks.StructBlock):
    richtext = AdvancedRichTextBlock(required=False)
    multimedia = blocks.StreamBlock(
        [
            ("link_card", LinkCardBlock()),
            ("video", VideoBlock())
        ]
    )

    class Meta:
        label = "Multimedia Row"
        template = "patterns/molecules/streamfield/blocks/multimedia_block.html"


class FreeFormBlocks(FreeFormBlocksBase):
    rich_text = RichTextBlock(group="Base")
    rich_text_advanced = AdvancedRichTextBlock(group="Base")
    image = ImageBlock(group="Base")
    document = DocumentBlock(group="Base")
    accordion = AccordionBlock(group="Base")

    articles = ArticleCardsBlock(group="Module")
    embassy_story = EmbassyStory(group="Module")
    featured_articles = FeaturedArticlesBlock(group="Module")
    featured_story = FeaturedStoryBlock(group="Module")
    logos = LogoCardsBlock(group="Module")
    link_card = LinkCardsBlock()
    link_button = LinkButtonBlock()
    link_box = LinkBoxesBlock()
    table = TableBlock(table_options={'renderer': 'html'}, group="HTML")
    html = blocks.RawHTMLBlock(
        group="HTML",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
    )
    stats_block = StatsBlock(group="Base")
    multimedia_row = MultimediaRowBlock(group="Base")


class AdvancedRichtextSnippetBlock(blocks.StructBlock):
    AdvancedRichtext = SnippetChooserBlock(target_model="utils.AdvancedRichtextSnippet")

    class Meta:
        label = "Text Snippet"
        template = "patterns/molecules/streamfield/blocks/advanced_richtext_block.html"

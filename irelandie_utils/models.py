# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    FieldRowPanel,
    HelpPanel, TabbedInterface, ObjectList,
)
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page, TranslatableMixin, PreviewableMixin
from wagtail.query import PageQuerySet

from wagtail.images import get_image_model_string
from wagtail.search import index

from wagtail.snippets.models import register_snippet
from wagtailmedia.edit_handlers import MediaChooserPanel

from irelandie_navigation.mixins import SocialMediaFieldsMixin
from irelandie_utils.blocks import (
    ArticleStoryBlock,
    AdvancedRichTextBlock,
    AccordionBlock,
    ContactBlock, MinimalArticleStoryBlock, GeneralContentBlocks, ImageBlock, LinkButtonsBlock
)
from irelandie_utils.cache import get_default_cache_control_decorator
from irelandie_utils.query import order_by_pk_position
import django.utils.timezone
from wagtail.models import DraftStateMixin, RevisionMixin
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.admin.panels import PublishingPanel
from taggit.models import TaggedItemBase
from taggit.managers import TaggableManager
from modelcluster.models import ClusterableModel

SEARCH_DESCRIPTION_LABEL = "Meta description"  # NOTE changing this requires migrations

IMAGE_MODEL = get_image_model_string()

ALT_HELP_TEXT = """A short one-sentence literal description
                    of the video/image is
                    required to make the page accessible to the
                    visually impaired. Details: https://axesslab.com/alt-texts/"""


class LinkFields(models.Model):
    """
    Adds fields for internal and external links with some methods to simplify the rendering:

    <a href="{{ obj.get_link_url }}">{{ obj.get_link_text }}</a>
    """

    link_page = models.ForeignKey(
        "wagtailcore.Page", blank=True, null=True, on_delete=models.SET_NULL
    )
    link_url = models.URLField(blank=True)
    link_text = models.CharField(blank=True, max_length=255)

    class Meta:
        abstract = True

    def clean(self):
        if not self.link_page and not self.link_url:
            raise ValidationError(
                {
                    "link_url": ValidationError(
                        "You must specify link page or link url."
                    ),
                    "link_page": ValidationError(
                        "You must specify link page or link url."
                    ),
                }
            )

        if self.link_page and self.link_url:
            raise ValidationError(
                {
                    "link_url": ValidationError(
                        "You must specify link page or link url. You can't use both."
                    ),
                    "link_page": ValidationError(
                        "You must specify link page or link url. You can't use both."
                    ),
                }
            )

        if not self.link_page and not self.link_text:
            raise ValidationError(
                {
                    "link_text": ValidationError(
                        "You must specify link text, if you use the link url field."
                    )
                }
            )

    def get_link_text(self):
        if self.link_text:
            return self.link_text

        if self.link_page:
            return self.link_page.title

        return ""

    def get_link_url(self):
        if self.link_page:
            return self.link_page.get_url

        return self.link_url

    panels = [
        MultiFieldPanel(
            [
                PageChooserPanel("link_page"),
                FieldPanel("link_url"),
                FieldPanel("link_text"),
            ],
            "Link",
        )
    ]


# Related pages
class PageRelatedPage(Orderable):
    parent = ParentalKey(Page, related_name="page_related_pages")
    page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [PageChooserPanel("page")]


# Related pages
class PageRelatedTags(Orderable):
    parent = ParentalKey(Page, related_name="page_related_tags")
    page = models.ForeignKey(
        "irelandie_tags.TagPage",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [PageChooserPanel("page")]


class PageRelatedDestinationTags(Orderable):
    parent = ParentalKey(Page, related_name="page_related_destination_tags")
    page = models.ForeignKey(
        "irelandie_tags.DestinationTagPage",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [PageChooserPanel("page")]


class PageRelatedDestinations(Orderable):
    parent = ParentalKey(Page, related_name="page_related_destinations")
    page = models.ForeignKey(
        "irelandie_missions.DestinationPage",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [PageChooserPanel("page")]


# Generic social fields abstract class to add social image/text to any new content type easily.
class SocialFields(models.Model):
    social_image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    social_text = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            [FieldPanel("social_image", permission="access_admin"),
             FieldPanel("social_text", permission="access_admin")],
            "Social networks",
        )
    ]


# Generic listing fields abstract class to add listing image/text to any new content type easily.
class ListingFields(models.Model):
    listing_image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose the image you wish to be displayed when this page appears in listings",
    )
    listing_image_alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Listing Image Alt text")
    )
    listing_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Override the page title used when this page appears in listings",
    )
    listing_summary = models.CharField(
        max_length=255,
        blank=True,
        help_text="The text summary used when this page appears in listings. It's also used as "
                  f"the description for search engines if the '{SEARCH_DESCRIPTION_LABEL}' field above is not defined.",
    )

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("listing_image", permission="access_admin"),
                FieldPanel(
                    "listing_image_alt",
                    help_text=_("The alt text shown for accessibility: https://axesslab.com/alt-texts/"),
                    permission="access_admin"
                ),
                FieldPanel("listing_title", permission="access_admin"),
                FieldPanel("listing_summary", permission="access_admin"),
            ],
            "Listing information",
        )
    ]


class ContactSnippetTag(TaggedItemBase):
    content_object = ParentalKey('utils.ContactSnippet', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class ContactSnippet(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, models.Model):
    tags = TaggableManager(through=ContactSnippetTag, blank=True)
    title = models.CharField(max_length=255)
    body = StreamField(
        [
            ("contact_details", ContactBlock()),
        ],
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="contactnnippet")

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/contactsnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


class CallToActionSnippetTag(TaggedItemBase):
    content_object = ParentalKey('utils.CallToActionSnippet', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class CallToActionSnippet(DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, models.Model):
    tags = TaggableManager(through=CallToActionSnippetTag, blank=True)
    title = models.CharField(max_length=255)
    summary = RichTextField(blank=True, max_length=255)
    image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Image Alt text"),
        help_text=_("The alt text shown for accessibility: https://axesslab.com/alt-texts/")
    )

    link = StreamField(
        blocks.StreamBlock(
            [
                (
                    "external_link",
                    blocks.StructBlock(
                        [("url", blocks.URLBlock()), ("title", blocks.CharBlock())],
                        icon="link",
                    ),
                ),
                (
                    "internal_link",
                    blocks.StructBlock(
                        [
                            ("page", blocks.PageChooserBlock()),
                            ("title", blocks.CharBlock(required=False)),
                        ],
                        icon="link",
                    ),
                ),
            ],
            max_num=1,
        ),
        blank=True,
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="calltoactionsnippet")

    panels = [
        FieldPanel("title"),
        FieldPanel("summary"),
        MultiFieldPanel([
            FieldPanel("image"),
            FieldPanel("image_alt"),
        ], heading="Image"),
        FieldPanel("link"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    @property
    def revisions(self):
        return self._revisions

    def get_link_text(self):
        # Link is required, so we should always have
        # an element with index 0
        block = self.link[0]

        title = block.value["title"]
        if block.block_type == "external_link":
            return title

        # Title is optional for internal_link
        # so fallback to page's title, if it's empty
        return title or block.value["page"].title

    def get_link_url(self):
        # Link is required, so we should always have
        # an element with index 0
        block = self.link[0]

        if block.block_type == "external_link":
            return block.value["url"]

        return block.value["page"].get_url()

    def __str__(self):
        return self.title


class PrivacyPolicySnippetTag(TaggedItemBase):
    content_object = ParentalKey('utils.PrivacyPolicySnippet', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class PrivacyPolicySnippet(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel,
                           models.Model):
    tags = TaggableManager(through=PrivacyPolicySnippetTag, blank=True)
    title = models.CharField(max_length=255)
    privacy_snippet = StreamField(
        [
            ("privacy_policy", AdvancedRichTextBlock()),
        ],
        blank=True,
        null=True,
        max_num=1,
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="privacypolicysnippet")
    panels = [
        FieldPanel("title"),
        FieldPanel("privacy_snippet"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/privacypolicysnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


class AdvancedRichtextSnippetTag(TaggedItemBase):
    content_object = ParentalKey('utils.AdvancedRichtextSnippet', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class AdvancedRichtextSnippet(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel,
                              models.Model):
    tags = TaggableManager(through=AdvancedRichtextSnippetTag, blank=True)
    title = models.CharField(max_length=255)
    advanced_rich_text = StreamField(
        [
            ("advanced_rich_text", AdvancedRichTextBlock()),
        ],
        blank=True,
        null=True,
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="advancedrichtextsnippet")
    panels = [
        FieldPanel("title"),
        FieldPanel("advanced_rich_text"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/advancedrichtextsnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


class EmbassySnippetTag(TaggedItemBase):
    content_object = ParentalKey('utils.EmbassySnippet', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class EmbassySnippet(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel,
                     models.Model):
    tags = TaggableManager(through=EmbassySnippetTag, blank=True)
    title = models.CharField(max_length=255)
    advanced_rich_text = StreamField(
        [
            ("advanced_rich_text", AdvancedRichTextBlock()),
        ],
        blank=True,
        null=True,
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="embassysnippet")
    panels = [
        FieldPanel("title"),
        FieldPanel("advanced_rich_text"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/advancedrichtextsnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


class AccordionTag(TaggedItemBase):
    content_object = ParentalKey('utils.Accordion', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class Accordion(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, models.Model):
    tags = TaggableManager(through=AccordionTag, blank=True)
    title = models.CharField(max_length=255)
    accordions = StreamField(
        [
            ("accordions", AccordionBlock()),
        ],
        blank=True,
        null=True,
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="accordion")
    panels = [
        FieldPanel("title"),
        FieldPanel("accordions", permission="access_admin"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/accordionsnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


@register_setting
class SocialMediaSettings(SocialMediaFieldsMixin, BaseSetting):
    # social media fields come from the SocialMediaFieldsMixin
    default_sharing_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Default sharing text to use if social text has not been set on a page.",
    )
    site_name = models.CharField(
        max_length=255,
        blank=True,
        default="Ireland.ie",
        help_text="Site name, used by Open Graph.",
    )


@register_setting
class SystemMessagesSettings(BaseSetting):
    class Meta:
        verbose_name = "system messages"

    title_404 = models.CharField("Title", max_length=255, default="Page not found")
    body_404 = RichTextField(
        "Text",
        default="<p>You may be trying to find a page that doesn&rsquo;t exist or has been moved.</p>",
    )

    panels = [
        MultiFieldPanel([FieldPanel("title_404"), FieldPanel("body_404")], "404 page")
    ]


# Apply default cache headers on this page model's serve method.
@method_decorator(get_default_cache_control_decorator(), name="serve")
class BasePage(SocialFields, ListingFields, Page):
    show_in_menus_default = True

    webchat_script = models.TextField(
        blank=True,
    )

    web_bot_script = models.TextField(
        blank=True,
    )

    webchat_panel = [
        MultiFieldPanel([
            FieldPanel("webchat_script", permission="access_admin"),
            FieldPanel("web_bot_script", permission="access_admin"),
        ], "Chatbot")
    ]

    custom_footer = models.ForeignKey(
        "irelandie_navigation.CustomFooter",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    custom_footer_panel = [
        FieldPanel("custom_footer", permission="access_admin")
    ]

    custom_header = models.ForeignKey(
        "irelandie_navigation.CustomHeader",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    custom_header_panel = [
        FieldPanel("custom_header", permission="access_admin")
    ]

    class Meta:
        abstract = True

    COMMON_PROMOTE_PANELS = (
        FieldPanel('slug', permission="access_admin"),
        FieldPanel('seo_title', permission="access_admin"),
        FieldPanel('search_description', permission="access_admin"),
    )

    promote_panels = (
        [
            MultiFieldPanel(COMMON_PROMOTE_PANELS, heading="For search engines"),
            FieldPanel('show_in_menus', permission="access_admin"),
        ] +
        SocialFields.promote_panels +
        ListingFields.promote_panels
    )
    settings_panels = ([
                           MultiFieldPanel(
                               [
                                   FieldPanel('go_live_at', permission="access_admin"),
                                   FieldPanel('expire_at', permission="access_admin"),
                               ],
                               "Scheduled publishing"
                           ),
                           MultiFieldPanel(
                               [
                                   FieldPanel("custom_header", permission="access_admin"),
                                   FieldPanel("custom_footer", permission="access_admin")
                               ],
                               "Root Navigation"
                           ),
                       ] +
                       webchat_panel
                       )

    search_fields = Page.search_fields + [
        index.SearchField("listing_title"),
        index.SearchField("listing_summary"),
    ]

    @cached_property
    def related_destination_tags(self) -> PageQuerySet:
        """
        Return a `PageQuerySet` of items related to this page via the
        `PageRelatedPage` through model, and are suitable for display.
        The result is ordered to match that specified by editors using
        the 'page_related_pages' `InlinePanel`.
        """

        # NOTE: avoiding values_list() here for compatibility with preview
        # See: https://github.com/wagtail/django-modelcluster/issues/30
        ordered_page_pks = tuple(item.page_id for item in self.page_related_destination_tags.all())
        return order_by_pk_position(
            Page.objects.live().public().specific(),
            pks=ordered_page_pks,
            exclude_non_matches=True,
        )

    @cached_property
    def related_destinations(self) -> PageQuerySet:
        """
        Return a `PageQuerySet` of items related to this page via the
        `PageRelatedPage` through model, and are suitable for display.
        The result is ordered to match that specified by editors using
        the 'page_related_pages' `InlinePanel`.
        """

        # NOTE: avoiding values_list() here for compatibility with preview
        # See: https://github.com/wagtail/django-modelcluster/issues/30
        ordered_page_pks = tuple(item.page_id for item in self.page_related_destinations.all())
        return order_by_pk_position(
            Page.objects.live().public().specific(),
            pks=ordered_page_pks,
            exclude_non_matches=True,
        )

    @cached_property
    def related_tags(self) -> PageQuerySet:
        """
        Return a `PageQuerySet` of items related to this page via the
        `PageRelatedPage` through model, and are suitable for display.
        The result is ordered to match that specified by editors using
        the 'page_related_pages' `InlinePanel`.
        """

        # NOTE: avoiding values_list() here for compatibility with preview
        # See: https://github.com/wagtail/django-modelcluster/issues/30
        ordered_page_pks = tuple(item.page_id for item in self.page_related_tags.all())
        return order_by_pk_position(
            Page.objects.live().public().specific(),
            pks=ordered_page_pks,
            exclude_non_matches=True,
        )

    @cached_property
    def related_pages(self) -> PageQuerySet:
        """
        Return a `PageQuerySet` of items related to this page via the
        `PageRelatedPage` through model, and are suitable for display.
        The result is ordered to match that specified by editors using
        the 'page_related_pages' `InlinePanel`.
        """

        # NOTE: avoiding values_list() here for compatibility with preview
        # See: https://github.com/wagtail/django-modelcluster/issues/30
        ordered_page_pks = tuple(item.page_id for item in self.page_related_pages.all())
        return order_by_pk_position(
            Page.objects.live().public().specific(),
            pks=ordered_page_pks,
            exclude_non_matches=True,
        )

    @cached_property
    def custom_primary_navigation(self):
        from irelandie_missions.models import CountryGroupPageIndex

        country_index = (
            Page.objects.ancestor_of(self, inclusive=True)
            .exact_type(CountryGroupPageIndex)
            .first()
        )
        if country_index:
            return country_index.specific.override_primary_navigation
        return None


BasePage._meta.get_field("seo_title").verbose_name = "Title tag"
BasePage._meta.get_field("search_description").verbose_name = SEARCH_DESCRIPTION_LABEL


@register_setting(icon="view")
class Tracking(BaseSetting):
    google_tag_manager_id = models.CharField(
        max_length=255,
        blank="True",
        help_text="Your Google Tag Manager ID",
    )


class HeroPage(BasePage):
    hero_title = models.CharField(blank=True, max_length=120)
    hero_image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_video = models.ForeignKey(
        "wagtailmedia.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_image_credit = models.CharField(blank=True, max_length=255)
    alt_text = models.CharField(blank=True,
                                null=True,
                                max_length=255,
                                help_text=ALT_HELP_TEXT)
    summary = models.CharField(blank=True, max_length=255)
    link_page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    link_text = models.CharField(blank=True, max_length=255)
    secondary_title = models.CharField(blank=True, max_length=255)
    hexcolor = models.CharField(max_length=7, blank=True)
    transparency = models.PositiveIntegerField(null=True, blank=True)

    def clean(self):
        if self.hero_image and self.hero_video:
            raise ValidationError(
                {
                    "hero_image": ValidationError(
                        "You can't choose both an image and a video for the hero media. Choose an image or a video"
                    ),
                    "hero_video": ValidationError(
                        "You can't choose both an image and a video for the hero media. Choose an image or a video"
                    ),
                }
            )

        if self.link_page and not self.link_text:
            raise ValidationError(
                {
                    "link_text": ValidationError(
                        "You must provide some Link text if you choose a link page"
                    )
                }
            )
        if self.hero_image and not self.alt_text:
            raise ValidationError(
                {
                    "alt_text": ValidationError(
                        "You must provide an alt_text."
                    )
                }
            )

        if self.transparency and self.transparency > 100:
            raise ValidationError(
                {
                    "transparency": ValidationError(
                        "Value must be less than or equal to 100"
                    )
                }
            )

    class Meta:
        abstract = True

    hero_panel = [
        HelpPanel("For the hero to display you must set the image or video field below."),
        FieldRowPanel([
            FieldPanel("hero_image", classname="col6"),
            MediaChooserPanel("hero_video", media_type="video", classname="col6"),
        ], "Hero Media"),
        FieldPanel("hero_image_credit"),
        FieldPanel("hero_title"),
        FieldPanel("alt_text"),
        FieldPanel("summary"),
        FieldPanel("transparency"),
        FieldPanel("hexcolor"),
        MultiFieldPanel(
            [
                HelpPanel("For the Call To Action to display you must set the Link text if you choose a Link Page."),
                PageChooserPanel("link_page"),
                FieldPanel("link_text"),
            ],
            "Call To Action",
        )]

    content_panels = Page.content_panels + [
        FieldPanel("secondary_title"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(hero_panel, heading='Hero'),
        ObjectList(BasePage.promote_panels, heading='Promote'),
        ObjectList(BasePage.settings_panels, heading='Settings', classname="settings"),
    ])


class ArticlePage(BasePage):
    introduction = models.TextField(blank=True)

    hero_image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_video = models.ForeignKey(
        "wagtailmedia.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_image_credit = models.CharField(blank=True, null=True, max_length=255)

    body = StreamField(ArticleStoryBlock(), blank=True)

    call_to_action = models.ForeignKey(
        CallToActionSnippet,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    related_articles_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                FieldPanel("hero_image_credit"),
                MediaChooserPanel("hero_video", media_type="video"),
            ],
            "hero",
        ),
        FieldPanel("call_to_action"),
        FieldPanel("body"),
        FieldPanel("related_articles_active"),
        FieldPanel("override_related_articles"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
    ]

    def clean(self):
        if self.hero_image and self.hero_video:
            raise ValidationError(
                {
                    "hero_image": ValidationError(
                        "You can't choose both an image and a video for the hero media. Choose an image or a video"
                    ),
                    "hero_video": ValidationError(
                        "You can't choose both an image and a video for the hero media. Choose an image or a video"
                    ),
                }
            )

    @property
    def override_related_articles(self):
        raise NotImplementedError

    @cached_property
    def related_articles(self):
        if self.override_related_articles:
            return [
                article.value
                for article in self.override_related_articles
                if article.value.live
            ]

        return (
            Page.objects.exact_type(type(self))
            .child_of(self.get_parent())
            .filter(locale=self.locale)
            .exclude(pk=self.pk)
            .public()
            .live()
            .order_by("-first_published_at")[:3]
            .specific()
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from irelandie_missions.models import MissionPage
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = MissionPage.objects.live().get(id=p.id)
                if missions.root_page:
                    context['default_image'] = missions.default_image

        return context


class MinimalArticlePage(BasePage):
    introduction = models.TextField(blank=True)
    subtitle = models.TextField(blank=True, help_text="Please include a brief description of this page/article. This "
                                                      "will not appear live on the page, but will appear publicly as "
                                                      "a subtitle in other areas of the site that link to this page.")

    hero_image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    alt_text = models.CharField(blank=True,
                                null=True,
                                max_length=255,
                                help_text=ALT_HELP_TEXT)
    hero_image_credit = models.CharField(blank=True, null=True, max_length=255)
    caption = models.CharField(blank=True,
                               null=True,
                               max_length=255, )

    publication_date = models.DateTimeField(default=django.utils.timezone.now)

    body = StreamField(MinimalArticleStoryBlock(), blank=True)

    related_articles_active = models.BooleanField(default=True)
    featured_home = models.BooleanField(default=False)

    class Meta:
        abstract = True

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("subtitle"),

        MultiFieldPanel(
            [
                FieldPanel("hero_image", heading="Featured Image"),
                FieldPanel("alt_text"),
                FieldPanel("hero_image_credit"),
                FieldPanel("caption"),
            ],
            "hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel('go_live_at'),
                FieldPanel('expire_at'),
            ],
            "Scheduled publishing"
        ),
        FieldPanel("publication_date"),
        FieldPanel("body"),
        FieldPanel("related_articles_active", heading="Featured News Checkbox"),
        FieldPanel("featured_home", heading="Featured Home", 
                   help_text="Checking this box will feature this news item on your mission/microsite "
                            "homepage if pinned stories are enabled.")
    ]

    settings_panels = ([
                           MultiFieldPanel(
                               [
                                   FieldPanel("custom_header", permission="access_admin"),
                                   FieldPanel("custom_footer", permission="access_admin")
                               ],
                               "Root Navigation"
                           ),
                       ] +
                       BasePage.webchat_panel
                       )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(BasePage.promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])

    def clean(self):
        if self.hero_image and not self.alt_text:
            raise ValidationError(
                {
                    "alt_text": ValidationError(
                        "You must provide an alt_text."
                    )
                }
            )


class CountryGroupTag(TaggedItemBase):
    content_object = ParentalKey('utils.CountryGroup', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class CountryGroup(DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, models.Model):
    tags = TaggableManager(through=CountryGroupTag, blank=True)
    title = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=100)
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="CountryGroup")

    panels = [
        FieldPanel("title"),
        FieldPanel("region"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.region


class TwitterEmbedTag(TaggedItemBase):
    content_object = ParentalKey('utils.TwitterEmbed', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class TwitterEmbed(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, TranslatableMixin,
                   models.Model):
    tags = TaggableManager(through=TwitterEmbedTag, blank=True)
    title = models.CharField(
        max_length=255,
        blank=True,
    )
    username = models.CharField(
        max_length=100,
        help_text="Twitter username",
    )
    width = models.PositiveIntegerField(
        default=0,
        help_text="Width of the embedded tweet panel in pixels",
    )
    height = models.PositiveIntegerField(
        default=0,
        help_text="Height of the embedded tweet panel in pixels",
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="twitterEmbed")

    panels = [
        FieldPanel("title"),
        FieldPanel("username"),
        MultiFieldPanel([
            HelpPanel("A value of 0 will display the tweet panel as a full width component."),
            FieldPanel("width"),
            FieldPanel("height"),
        ], heading="Dimensions"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.FilterField('locale_id'),
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/twitterembedsnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        if not self.title:
            return f"{self.username} (username)"
        return self.title

    class Meta:
        unique_together = ('translation_key', 'locale')


class VisaTag(TaggedItemBase):
    content_object = ParentalKey('utils.Visa', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class Visa(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, models.Model):
    tags = TaggableManager(through=VisaTag, blank=True)
    title = models.CharField(max_length=255)
    body = StreamField(
        [
            ("content", GeneralContentBlocks())
        ],
        blank=True
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="visa")
    panels = [
        FieldPanel("title"),
        FieldPanel("body", permission="access_admin"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/general_block_snippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


class PassportTag(TaggedItemBase):
    content_object = ParentalKey('utils.Passport', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class Passport(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, models.Model):
    tags = TaggableManager(through=PassportTag, blank=True)
    title = models.CharField(max_length=255)
    body = StreamField(
        [
            ("content", GeneralContentBlocks())
        ],
        blank=True
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="passport")
    panels = [
        FieldPanel("title"),
        FieldPanel("body", permission="access_admin"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/general_block_snippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


class AuthenticationTag(TaggedItemBase):
    content_object = ParentalKey('utils.Authentication', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class Authentication(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, models.Model):
    tags = TaggableManager(through=AuthenticationTag, blank=True)
    title = models.CharField(max_length=255)
    body = StreamField(
        [
            ("content", GeneralContentBlocks())
        ],
        blank=True
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="authentication")
    panels = [
        FieldPanel("title"),
        FieldPanel("body", permission="access_admin"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/general_block_snippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


class MarriageTag(TaggedItemBase):
    content_object = ParentalKey('utils.Marriage', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class Marriage(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, models.Model):
    tags = TaggableManager(through=MarriageTag, blank=True)
    title = models.CharField(max_length=255)
    body = StreamField(
        [
            ("content", GeneralContentBlocks())
        ],
        blank=True
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="marriage")
    panels = [
        FieldPanel("title"),
        FieldPanel("body", permission="access_admin"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/general_block_snippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


class TravelSnippetTag(TaggedItemBase):
    content_object = ParentalKey('utils.TravelSnippet', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class TravelSnippet(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel, models.Model):
    tags = TaggableManager(through=TravelSnippetTag, blank=True)
    title = models.CharField(max_length=255)
    body = StreamField(
        [
            ("advanced_rich_text", AdvancedRichTextBlock()),
            ("link_buttons", LinkButtonsBlock()),
            ("image", ImageBlock()),
        ],
        blank=True
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="travelsnippet")
    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/travel_snippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title


class BetaSnippetTag(TaggedItemBase):
    content_object = ParentalKey('utils.BetaSnippet', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class BetaSnippet(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel,
                  models.Model):
    tags = TaggableManager(through=BetaSnippetTag, blank=True)
    title = models.CharField(max_length=255)
    rich_text = RichTextField(features=["h3", "h4", "h5", "bold", "italic", "link", "document-link"],
                              blank=True, null=True)
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="betasnippet")
    panels = [
        FieldPanel("title"),
        FieldPanel("rich_text"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/betasnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title

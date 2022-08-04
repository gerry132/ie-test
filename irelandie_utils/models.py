# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
    FieldRowPanel,
    HelpPanel, TabbedInterface, ObjectList,
)
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page, TranslatableMixin
from wagtail.core.query import PageQuerySet
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images import get_image_model_string
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from wagtailmedia.edit_handlers import MediaChooserPanel

from irelandie_navigation.mixins import SocialMediaFieldsMixin
from irelandie_utils.blocks import ArticleStoryBlock
from irelandie_utils.cache import get_default_cache_control_decorator
from irelandie_utils.query import order_by_pk_position

SEARCH_DESCRIPTION_LABEL = "Meta description"  # NOTE changing this requires migrations

IMAGE_MODEL = get_image_model_string()


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
            [ImageChooserPanel("social_image"), FieldPanel("social_text")],
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
                ImageChooserPanel("listing_image"),
                FieldPanel(
                    "listing_image_alt",
                    help_text=_("The alt text shown for accessibility: https://axesslab.com/alt-texts/")
                ),
                FieldPanel("listing_title"),
                FieldPanel("listing_summary"),
            ],
            "Listing information",
        )
    ]


@register_snippet
class CallToActionSnippet(models.Model):
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

    panels = [
        FieldPanel("title"),
        FieldPanel("summary"),
        MultiFieldPanel([
            ImageChooserPanel("image"),
            FieldPanel("image_alt"),
        ], heading="Image"),
        StreamFieldPanel("link"),
    ]

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
            FieldPanel("webchat_script"),
            FieldPanel("web_bot_script"),
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
        SnippetChooserPanel("custom_footer")
    ]

    custom_header = models.ForeignKey(
        "irelandie_navigation.CustomHeader",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    custom_header_panel = [
        SnippetChooserPanel("custom_header")
    ]

    class Meta:
        abstract = True

    promote_panels = (
        Page.promote_panels +
        SocialFields.promote_panels +
        ListingFields.promote_panels +
        webchat_panel +
        custom_footer_panel +
        custom_header_panel
    )

    search_fields = Page.search_fields + [
        index.SearchField("listing_title"),
        index.SearchField("listing_summary"),
    ]

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
            ImageChooserPanel("hero_image", classname="col6"),
            MediaChooserPanel("hero_video", media_type="video", classname="col6"),
        ], "Hero Media"),
        FieldPanel("hero_title"),
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

    body = StreamField(ArticleStoryBlock(), blank=True)

    call_to_action = models.ForeignKey(
        CallToActionSnippet,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        abstract = True

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel(
            [
                ImageChooserPanel("hero_image"),
                MediaChooserPanel("hero_video", media_type="video"),
            ],
            "hero",
        ),
        SnippetChooserPanel("call_to_action"),
        StreamFieldPanel("body"),
        StreamFieldPanel("override_related_articles"),
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
            .filter(locale=self.locale)
            .exclude(pk=self.pk)
            .public()  # type:ignore
            .live()
            .order_by("-first_published_at")[:3]
            .specific()
        )


@register_snippet
class CountryGroup(models.Model):
    region = models.CharField(max_length=100)

    def __str__(self):
        return self.region


@register_snippet
class TwitterEmbed(TranslatableMixin, models.Model):
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

    panels = [
        FieldPanel("title"),
        FieldPanel("username"),
        MultiFieldPanel([
            HelpPanel("A value of 0 will display the tweet panel as a full width component."),
            FieldPanel("width"),
            FieldPanel("height"),
        ], heading="Dimensions"),
    ]

    def __str__(self):
        if not self.title:
            return f"{self.username} (username)"
        return self.title

# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import TranslatableMixin, PreviewableMixin

from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet

from .blocks import (
    LinkBlockExtended,
    LinkColumnWithHeader,
    SecondaryNavLinkColumnWithHeader,
)
from irelandie_navigation.mixins import SocialMediaFieldsMixin
from wagtail.models import DraftStateMixin, RevisionMixin
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.admin.panels import PublishingPanel
from wagtail.search import index
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from taggit.managers import TaggableManager

IMAGE_MODEL = get_image_model_string()

ALT_HELP_TEXT = """A short one-sentence literal description
                    of the %s is
                    required to make the page accessible to the
                    visually impaired. Details: https://axesslab.com/alt-texts/"""

ALT_VID = ALT_HELP_TEXT % 'video'
ALT_IMAGE = ALT_HELP_TEXT % 'image'


@register_setting(icon="list-ul")
class SiteSettings(BaseSetting, ClusterableModel):
    # The settings here are currently unused.
    # We may be removing it in the future.
    favicon = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    site_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    mobile_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    site_logo_alt = models.CharField(
        max_length=255,
        blank=False,
        verbose_name=_("Logo Alt text"),
        help_text=_(ALT_IMAGE),
    )

    google_my_map = models.TextField(
        blank=True,
        help_text=_("Iframe code for Google My Maps."),
    )

    panels = [
        MultiFieldPanel([
            FieldPanel("favicon"),
            FieldPanel("site_logo"),
            FieldPanel("mobile_logo"),
            FieldPanel("site_logo_alt"),
            FieldPanel("google_my_map"),
        ], heading="Site Logo"),
    ]


class PrimaryNavigationTag(TaggedItemBase):
    content_object = ParentalKey('irelandie_navigation.PrimaryNavigation', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class PrimaryNavigation(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel,
                        TranslatableMixin):
    # Snippets model is used so the navigation can be localised with TranslatableMixin.
    tags = TaggableManager(through=PrimaryNavigationTag, blank=True)
    title = models.CharField(max_length=255, blank=True)

    lang = models.CharField(
        max_length=255,
        unique=True,
        help_text="Internal name for this navigation, it's not displayed to a site user.",
        verbose_name=_("Language"),
    )
    navigation = StreamField(
        [("link", LinkBlockExtended())],
        blank=True,
        help_text="Main site navigation",
        verbose_name=_("Links"),
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="primarynavigation")

    panels = [
        FieldPanel("title"),
        MultiFieldPanel(
            [
                FieldPanel("lang"),
                FieldPanel("navigation"),
            ],
            heading=_("Primary Navigation"),
        ),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.FilterField('locale_id'),
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/customheadersnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.lang

    class Meta:
        verbose_name = _("Primary Navigation")
        verbose_name_plural = _("Primary Navigation")
        unique_together = ("translation_key", "locale")


class FooterNavigationTag(TaggedItemBase):
    content_object = ParentalKey('irelandie_navigation.FooterNavigation', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class FooterNavigation(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel,
                       TranslatableMixin):
    # Snippets model is used so the navigation can be localised with TranslatableMixin.
    tags = TaggableManager(through=FooterNavigationTag, blank=True)
    title = models.CharField(max_length=255, blank=True)
    lang = models.CharField(
        max_length=255,
        unique=True,
        help_text="Internal name for this navigation, it's not displayed to a site user.",
        verbose_name=_("Language"),
    )
    navigation = StreamField(
        [("column", LinkColumnWithHeader())],
        blank=True,
        help_text="Multiple columns of footer links with optional header.",
        verbose_name=_("Columns"),
    )
    links = StreamField(
        [("link", LinkBlockExtended())],
        blank=True,
        help_text=_("Single list of elements at the base of the page."),
    )
    email_address = models.EmailField(
        max_length=255,
        blank=True,
        verbose_name=_("email address"),
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="footernavigation")

    panels = [
        FieldPanel("title"),
        MultiFieldPanel(
            [
                FieldPanel("lang"),
                FieldPanel("navigation"),
                FieldPanel("links"),
                FieldPanel("email_address"),
            ],
            heading=_("Footer Navigation"),
        ),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.FilterField('locale_id'),
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/customfootersnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.lang

    class Meta:
        verbose_name = _("Footer Navigation")
        verbose_name_plural = _("Footer Navigation")
        unique_together = ("translation_key", "locale")


class SecondaryNavigationTag(TaggedItemBase):
    content_object = ParentalKey('irelandie_navigation.SecondaryNavigation', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class SecondaryNavigation(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel,
                          TranslatableMixin):
    # Snippets model is used so the navigation can be localised with TranslatableMixin.
    tags = TaggableManager(through=SecondaryNavigationTag, blank=True)
    title = models.CharField(max_length=255, blank=True)
    lang = models.CharField(
        max_length=255,
        unique=True,
        help_text="Internal name for this navigation, it's not displayed to a site user.",
        verbose_name=_("Language"),
    )
    navigation = StreamField(
        [("column", SecondaryNavLinkColumnWithHeader())],
        blank=True,
        help_text="Multiple columns of links with optional header.",
        verbose_name=_("Columns"),
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="cecondarynavigation")

    panels = [
        FieldPanel("title"),
        MultiFieldPanel(
            [
                FieldPanel("lang"),
                FieldPanel("navigation"),
            ],
            heading=_("Secondary Navigation"),
        ),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.FilterField('locale_id'),
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/secondarynavsnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.lang

    class Meta:
        verbose_name = _("Secondary Navigation")
        verbose_name_plural = _("Secondary Navigation")
        unique_together = ("translation_key", "locale")


class CustomFooterTag(TaggedItemBase):
    content_object = ParentalKey('irelandie_navigation.CustomFooter', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class CustomFooter(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel,
                   SocialMediaFieldsMixin, TranslatableMixin):
    # Snippets model is used so the navigation can be localised with TranslatableMixin.
    tags = TaggableManager(through=CustomFooterTag, blank=True)
    title = models.CharField(max_length=255, blank=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Internal name for this navigation, it's not displayed to a site user.",
        verbose_name=_("Name"),
    )
    navigation = StreamField(
        [("column", LinkColumnWithHeader())],
        blank=True,
        help_text="Multiple columns of footer links with optional header.",
        verbose_name=_("Columns"),
    )
    links = StreamField(
        [("link", LinkBlockExtended())],
        blank=True,
        help_text=_("Single list of elements at the base of the page."),
    )
    logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    mobile_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    logo_alt = models.CharField(
        max_length=255,
        blank=False,
        verbose_name=_("Logo Alt text"),
        help_text=_(ALT_IMAGE),
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="customfooter")

    panels = [
        FieldPanel("title"),
        MultiFieldPanel([
            FieldPanel("logo"),
            FieldPanel("mobile_logo"),
            FieldPanel("logo_alt"),
        ], heading="Logo"),
        FieldPanel("name"),
        FieldPanel("twitter_handle"),
        FieldPanel("facebook_app_id"),
        FieldPanel("youtube_user"),
        FieldPanel("linkedin_profile"),
        FieldPanel("instagram_user"),
        FieldPanel("navigation"),
        FieldPanel("links"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.FilterField('locale_id'),
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/customfootersnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Custom Footer")
        verbose_name_plural = _("Custom Footers")
        unique_together = ("translation_key", "locale")


class CustomHeaderTag(TaggedItemBase):
    content_object = ParentalKey('irelandie_navigation.CustomHeader', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class CustomHeader(PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed, ClusterableModel,
                   TranslatableMixin):
    # Snippets model is used so the navigation can be localised with TranslatableMixin.
    tags = TaggableManager(through=CustomHeaderTag, blank=True)
    title = models.CharField(max_length=255, blank=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Internal name for this navigation, it's not displayed to a site user.",
        verbose_name=_("Name"),
    )
    url = models.URLField(
        blank=True,
        max_length=255,
        null=True,
        help_text="URL for logo click.",
        verbose_name=_("URL"),
    )
    link_page = StreamField(
        [("internal_link", LinkBlockExtended())],
        blank=True,
        max_num=1)
    links = StreamField(
        [("link", LinkBlockExtended())],
        blank=True,
        help_text="Custom main site navigation",
        verbose_name=_("Links"),
    )
    logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    mobile_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    logo_alt = models.CharField(
        max_length=255,
        blank=False,
        verbose_name=_("Logo Alt text"),
        help_text=_(ALT_IMAGE),
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="customheader")

    panels = [
        FieldPanel("title"),
        MultiFieldPanel([
            FieldPanel("logo"),
            FieldPanel("mobile_logo"),
            FieldPanel("logo_alt"),
            FieldPanel("url"),
            FieldPanel("link_page"),
        ], heading="Logo"),
        FieldPanel("name"),
        FieldPanel("links"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.FilterField('locale_id'),
        index.SearchField("title", partial_match=True),
    ]

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/customheadersnippet.html"

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.name

    def clean(self):
        if self.link_page and self.url:
            raise ValidationError(
                {
                    "link_page": ValidationError(
                        "You can't choose both an internal page and an external url."
                    ),
                    "url": ValidationError(
                        "You can't choose both an internal page and an external url."
                    ),
                }
            )

    class Meta:
        verbose_name = _("Custom Header")
        verbose_name_plural = _("Custom Headers")
        unique_together = ("translation_key", "locale")

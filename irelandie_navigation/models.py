# -*- coding: utf-8 -*-

from django.conf import settings as dj_settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.fields import StreamField
from wagtail.core.models import TranslatableMixin
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

from .blocks import LinkBlock, LinkColumnWithHeader, SecondaryNavLinkColumnWithHeader

IMAGE_MODEL = str(dj_settings.WAGTAILIMAGES_IMAGE_MODEL)


@register_setting(icon="list-ul")
class SiteSettings(BaseSetting, ClusterableModel):
    # The settings here are currently unused.
    # We may be removing it in the future.
    site_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    site_logo_alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Logo Alt text"),
        help_text=_("The alt text shown for accessibility: https://axesslab.com/alt-texts/"),
    )

    panels = [
        MultiFieldPanel([
            ImageChooserPanel("site_logo"),
            FieldPanel("site_logo_alt"),
        ], heading="Site Logo"),
    ]


@register_snippet
class PrimaryNavigation(TranslatableMixin):
    # Snippets model is used so the navigation can be localised with TranslatableMixin.
    lang = models.CharField(
        max_length=255,
        unique=True,
        help_text="Internal name for this navigation, it's not displayed to a site user.",
        verbose_name=_("Language"),
    )
    navigation = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Main site navigation",
        verbose_name=_("Links"),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("lang"),
                StreamFieldPanel("navigation"),
            ],
            heading=_("Primary Navigation"),
        )
    ]

    def __str__(self):
        return self.lang

    class Meta:
        verbose_name = _("Primary Navigation")
        verbose_name_plural = _("Primary Navigation")
        unique_together = ("translation_key", "locale")


@register_snippet
class FooterNavigation(TranslatableMixin):
    # Snippets model is used so the navigation can be localised with TranslatableMixin.
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
        [("link", LinkBlock())],
        blank=True,
        help_text=_("Single list of elements at the base of the page."),
    )
    email_address = models.EmailField(
        max_length=255,
        blank=True,
        verbose_name=_("email address"),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("lang"),
                StreamFieldPanel("navigation"),
                StreamFieldPanel("links"),
                FieldPanel("email_address"),
            ],
            heading=_("Footer Navigation"),
        )
    ]

    def __str__(self):
        return self.lang

    class Meta:
        verbose_name = _("Footer Navigation")
        verbose_name_plural = _("Footer Navigation")
        unique_together = ("translation_key", "locale")


@register_snippet
class SecondaryNavigation(TranslatableMixin):
    # Snippets model is used so the navigation can be localised with TranslatableMixin.
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

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("lang"),
                StreamFieldPanel("navigation"),
            ],
            heading=_("Secondary Navigation"),
        )
    ]

    def __str__(self):
        return self.lang

    class Meta:
        verbose_name = _("Secondary Navigation")
        verbose_name_plural = _("Secondary Navigation")
        unique_together = ("translation_key", "locale")

# -*- coding: utf-8 -*-
from django.conf import settings as dj_settings
from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel


IMAGE_MODEL = str(dj_settings.WAGTAILIMAGES_IMAGE_MODEL)


class LinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock()
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title", required=False
    )

    class Meta:
        template = ("patterns/molecules/navigation/blocks/menu_item.html",)


class LinkColumnWithHeader(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=False, help_text="Leave blank if no header required."
    )
    links = blocks.ListBlock(LinkBlock())

    class Meta:
        template = ("patterns/molecules/navigation/blocks/footer_column.html",)


@register_setting(icon="list-ul")
class NavigationSettings(BaseSetting, ClusterableModel):
    site_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    primary_navigation = StreamField(
        [("link", LinkBlock())], blank=True, help_text="Main site navigation"
    )
    footer_navigation = StreamField(
        [("column", LinkColumnWithHeader())],
        blank=True,
        help_text="Multiple columns of footer links with optional header.",
    )
    footer_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Single list of elements at the base of the page.",
    )
    footer_email = models.EmailField(
        max_length=255,
        blank=True,
        verbose_name='email address',
    )

    panels = [
        ImageChooserPanel("site_logo"),
        StreamFieldPanel("primary_navigation"),
        MultiFieldPanel(
            [
                StreamFieldPanel("footer_navigation"),
                StreamFieldPanel("footer_links"),
                FieldPanel('footer_email'),
            ],
            "Footer"
        )
    ]

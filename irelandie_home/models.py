# -*- coding: utf-8 -*-
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin

from irelandie_utils import blocks


class HomePage(Page, TranslatableMixin):
    template = "irelandie_assets/pages/home.html"

    # Only allow creating HomePages at the root level
    parent_page_types = ["wagtailcore.Page"]

    alerts = StreamField(
        [
            ("alerts", blocks.AlertBlock()),
        ],
        max_num=1,
        min_num=0,
        blank=True,
        null=True,
    )

    jumpboxes = StreamField(
        [("jumpbox", blocks.JumpboxBlock())],
        min_num=0,
        blank=True,
        null=True,
    )

    jumpboxes_with_image = StreamField(
        [("jumpbox", blocks.JumpboxWithImageBlock())],
        min_num=0,
        max_num=3,
        blank=True,
        null=True,
    )

    max_count = 1
    subpage_types = ["irelandie_missions.CountryGroupPageIndex"]

    content_panels = Page.content_panels + [
        StreamFieldPanel("alerts"),
        StreamFieldPanel("jumpboxes"),
        StreamFieldPanel("jumpboxes_with_image"),
    ]

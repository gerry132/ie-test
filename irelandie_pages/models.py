# -*- coding: utf-8 -*-
from django.db import models

from wagtail.fields import StreamField
from wagtail.admin.panels import TabbedInterface, ObjectList, StreamFieldPanel, FieldPanel, MultiFieldPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from irelandie_utils.models import HeroPage
from irelandie_utils.blocks import FreeFormBlocks


class FreeFormPageBase(HeroPage):
    """
    A page model that is free form and has access to all stream blocks.
    """

    body = StreamField(FreeFormBlocks(), blank=True)

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel("body"),
    ]

    hero_panel = HeroPage.hero_panel

    class Meta:
        abstract = True
        verbose_name = "Free Form Page"
        verbose_name_plural = "Free Form Pages"


class FreeFormPage(FreeFormPageBase):
    template = "patterns/pages/irelandie_pages/free_form_page.html"

    twitter_title = models.CharField(max_length=50, blank=True)

    twitter_feed = models.ForeignKey(
        "utils.TwitterEmbed",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )

    content_panels = FreeFormPageBase.content_panels + [
        MultiFieldPanel([
            FieldPanel("twitter_title"),
            SnippetChooserPanel("twitter_feed"),
        ], heading="Twitter feed"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(FreeFormPageBase.hero_panel, heading='Hero'),
        ObjectList(FreeFormPageBase.promote_panels, heading='Promote'),
        ObjectList(FreeFormPageBase.settings_panels, heading='Settings', classname="settings"),
    ])

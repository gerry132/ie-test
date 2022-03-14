# -*- coding: utf-8 -*-
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import TabbedInterface, ObjectList, StreamFieldPanel

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

    edit_handler = TabbedInterface([
        ObjectList(FreeFormPageBase.content_panels, heading='Content'),
        ObjectList(FreeFormPageBase.hero_panel, heading='Hero'),
        ObjectList(FreeFormPageBase.promote_panels, heading='Promote'),
        ObjectList(FreeFormPageBase.settings_panels, heading='Settings', classname="settings"),
    ])

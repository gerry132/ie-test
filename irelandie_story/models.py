# -*- coding: utf-8 -*-
from django.db import models
from irelandie_utils.models import HeroPage
from irelandie_utils.blocks import GenericHeroBlock
from .blocks import StoryPageBlock
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList


class StoryPage(HeroPage):
    template = "patterns/pages/missions/general_content_page.html"
    generic_hero = StreamField(
        [
            ("generic_hero", GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )


    introduction = models.TextField(blank=True)
    body = StreamField(StoryPageBlock(), blank=True)

    content_panels = HeroPage.content_panels + [
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("introduction"),
        FieldPanel("body"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel, heading='Hero'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])

    class Meta:
        verbose_name = "Story page"

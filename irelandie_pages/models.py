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
        verbose_name = "Free Form Page Base"
        verbose_name_plural = "Free Form Pages Base"


class FreeFormPage(FreeFormPageBase):
    template = "patterns/pages/irelandie_pages/free_form_page.html"

    root_page = models.BooleanField(default=True)
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

    settings_panels = (
        [
            FieldPanel("root_page", permission="access_admin"),
        ] +
        HeroPage.settings_panels

    )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(FreeFormPageBase.hero_panel, heading='Hero'),
        ObjectList(FreeFormPageBase.promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])

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

    class Meta:
        verbose_name = "Free Form Page"

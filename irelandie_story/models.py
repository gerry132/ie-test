# -*- coding: utf-8 -*-
from django.db import models
from irelandie_utils.models import HeroPage
from irelandie_utils.blocks import GenericHeroBlock
from .blocks import StoryPageBlock
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, InlinePanel


class StoryPage(HeroPage):
    template = "patterns/pages/missions/general_content_page.html"
    subtitle = models.TextField(blank=True)
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
        FieldPanel("subtitle", help_text="Please include a brief description of this page/article. This will not "
                                         "appear live on the page, but will appear publicly as a subtitle in other "
                                         "areas of the site that link to this page."),
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("introduction"),
        FieldPanel("body"),
        InlinePanel('page_related_tags', label="Related category tags"),
        InlinePanel('page_related_destination_tags', label="Related destination"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel, heading='Hero'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from irelandie_utils.templatetags.util_tags import get_tag_links
        from irelandie_utils.templatetags.util_tags import get_destination_tag_links
        destination_tags = self.related_destination_tags
        context["destination_tag_links"] = get_destination_tag_links(destination_tags)
        tag = self.related_tags
        tagging_links = get_tag_links(tag, self)[0]
        tags_no_links = get_tag_links(tag, self)[1]
        context["tagging_links"] = tagging_links
        context["tags_no_links"] = tags_no_links
        return context

    class Meta:
        verbose_name = "Story page"

# -*- coding: utf-8 -*-
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import StreamFieldPanel

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

    class Meta:
        abstract = True
        verbose_name = "Free Form Page"
        verbose_name_plural = "Free Form Pages"


class FreeFormPage(FreeFormPageBase):
    template = "patterns/pages/irelandie_pages/free_form_page.html"

    # subpage_types = [
    #     "irelandie_home.CampaignPage",
    #     "irelandie_home.TopicPage",

    #     "irelandie_contact_details.ContactDetailPageIndex",
    #     "irelandie_contact_details.ContactDetailPage",

    #     "irelandie_missions.CountryGroupPageIndex",
    #     "irelandie_missions.CountryPage",
    #     "irelandie_missions.MissionPage",
    #     "irelandie_missions.MissionSearchPage",

    #     "irelandie_news.NewsPage",

    #     "irelandie_pages.FreeFormPage",

    #     "irelandie_forms.FormPage",
    #     ""
    # ]

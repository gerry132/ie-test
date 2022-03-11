# -*- coding: utf-8 -*-
from wagtail.core.fields import StreamField

# from irelandie_missions.models import MissionPage
from irelandie_site_information.blocks import SiteInformationPageBlock
from irelandie_utils.models import BasePage, ArticlePage


class SiteInformationPageIndex(BasePage):
    template = "patterns/pages/irelandie_site_information/site_information_index.html"

    # parent_page_types = [MissionPage]
    # subpage_types = ["SiteInformationPage"]
    max_count_per_parent = 1


class SiteInformationPage(ArticlePage):
    template = "patterns/pages/irelandie_site_information/site_information_page.html"

    override_related_articles = StreamField(
        [
            ("article", SiteInformationPageBlock()),
        ],
        blank=True,
        max_num=3
    )

    # parent_page_types = [
    #     "SiteInformationPageIndex",
    # ]
    # subpage_types = []

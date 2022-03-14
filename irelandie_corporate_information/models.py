# -*- coding: utf-8 -*-
from wagtail.core.fields import StreamField

from irelandie_corporate_information.blocks import CorportateInformationPageBlock
# from irelandie_missions.models import MissionPage
from irelandie_utils.models import ArticlePage, BasePage


class CorportateInformationPageIndex(BasePage):
    template = "patterns/pages/irelandie_corporate_information/corportate_information_index.html"

    # parent_page_types = [MissionPage]
    # subpage_types = ["CorportateInformationPage"]
    max_count_per_parent = 1


class CorportateInformationPage(ArticlePage):
    template = "patterns/pages/irelandie_corporate_information/corportate_information_page.html"

    override_related_articles = StreamField(
        [
            ("article", CorportateInformationPageBlock()),
        ],
        blank=True,
        max_num=3
    )

    # parent_page_types = ["CorportateInformationPageIndex"]
    # subpage_types = []

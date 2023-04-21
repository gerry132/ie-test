# -*- coding: utf-8 -*-
from django.db import models
from django.forms import ValidationError
from irelandie_utils.models import BasePage
from irelandie_utils.blocks import GenericHeroBlock
from irelandie_missions.models import DestinationPage
from .blocks import StoryPageBlock
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList

from wagtail import blocks


class TagPage(BasePage):
    tag_label = models.TextField(blank=True)
    destination_tag = blocks.PageChooserBlock(required=False, page_type=DestinationPage)

    def clean(self):

        if self.tag_label and self.destination_tag:
            raise ValidationError(
                {
                    "tag_label": ValidationError(
                        "You must specify a tag label or a destination tag. You can't use both."
                    ),
                    "destination_tag": ValidationError(
                        "You must specify a tag label or a destination tag. You can't use both."
                    ),
                }
            )

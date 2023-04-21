# -*- coding: utf-8 -*-
from django.db import models
from django.forms import ValidationError
from irelandie_utils.models import BasePage
from irelandie_missions.models import DestinationPage

from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel

from wagtail import blocks


class TagPage(BasePage):
    tag_label = models.TextField(blank=True)
    destination_tag = StreamField(
        [
         ("destination_tag", blocks.PageChooserBlock(required=False, page_type=DestinationPage)),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    content_panels = BasePage.content_panels + [
        FieldPanel("tag_label"),
        FieldPanel("destination_tag"),
    ]

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

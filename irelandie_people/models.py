# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import (
    FieldPanel,
    PageChooserPanel,
    MultiFieldPanel,
)
from wagtail.fields import StreamField, RichTextField
from wagtail.models import Page, TranslatableMixin, PreviewableMixin, BootstrapTranslatableMixin

from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet
from irelandie_utils.blocks import CustomVideoChooserBlockAlt, StoryLinkBlock

from wagtail.models import DraftStateMixin, RevisionMixin
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.admin.panels import PublishingPanel
from wagtail.search import index
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from taggit.managers import TaggableManager
from modelcluster.models import ClusterableModel

from irelandie_utils.signals import snippet_published
from .blocks import PersonPageSectionBlock, RolePageSectionBlock

IMAGE_MODEL = get_image_model_string()


class PersonPageIndex(Page, TranslatableMixin):
    max_count_per_parent = 1


class PersonPage(Page, TranslatableMixin):
    # TODO: there is no person page template yet.
    description = models.TextField(blank=True)
    body = StreamField(
        [
            ("section", PersonPageSectionBlock()),
        ],
        blank=True,
        null=True,
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Image Alt text"),
        help_text=_("The alt text shown for accessibility: https://axesslab.com/alt-texts/")
    )
    countries = ParentalManyToManyField("irelandie_missions.DestinationPage", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        FieldPanel("body"),
        MultiFieldPanel([
            FieldPanel("image"),
            FieldPanel("image_alt"),
        ], heading="Image"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]


class RolePageIndex(Page, TranslatableMixin):
    max_count_per_parent = 1


class RolePage(Page, TranslatableMixin):
    PERSON_PAGE_MODEL = PersonPage

    description = models.TextField(blank=True)
    body = StreamField(
        [
            ("section", RolePageSectionBlock()),
        ],
        blank=True,
        null=True,
    )
    role_holder = models.ForeignKey(
        PERSON_PAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    countries = ParentalManyToManyField("irelandie_missions.DestinationPage", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        FieldPanel("description"),
        FieldPanel("body"),
        PageChooserPanel("role_holder"),
        FieldPanel("countries", widget=forms.CheckboxSelectMultiple),
    ]


class PersonTag(TaggedItemBase):
    content_object = ParentalKey('irelandie_people.Person', on_delete=models.CASCADE,
                                 related_name='tagged_items')


@register_snippet
class Person(TranslatableMixin, PreviewableMixin, DraftStateMixin, RevisionMixin, index.Indexed,
             ClusterableModel, models.Model):
    tags = TaggableManager(through=PersonTag, blank=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True)
    image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    video = StreamField(
        [
            ("video", CustomVideoChooserBlockAlt()),
        ],
        blank=True,
    )
    embassy_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    social_media_link = models.URLField(blank=True)
    social_media_text = models.CharField(
        max_length=255, blank=True, default="Connect with person on this social media"
    )
    address = RichTextField(blank=True)
    telephone = models.CharField(max_length=255, blank=True)
    opening_hours = RichTextField(blank=True)
    closure_dates = RichTextField(blank=True)
    emergency_contact_details = RichTextField(blank=True)
    our_services_url = models.URLField(blank=True)
    our_role_url = models.URLField(blank=True)

    alignment = models.CharField(
        choices=(("left", "Left"), ("right", "Right")), max_length=255, default="left"
    )
    background = models.CharField(
        choices=(("light", "Light"), ("dark", "Dark")), max_length=255, default="light"
    )
    links = StreamField(
        [
            ("link", StoryLinkBlock(min_num=0, max_num=6)),
        ],
        blank=True,
    )
    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="person")

    class Meta(TranslatableMixin.Meta):
        verbose_name = "Person"
        verbose_name_plural = "People"
        unique_together = ('translation_key', 'locale')

    def __str__(self):
        return self.name

    panels = [
        FieldPanel("name", classname="full title"),
        FieldPanel("title"),
        MultiFieldPanel(
            [
                FieldPanel("alignment"),
                FieldPanel("image"),
                FieldPanel("video"),
            ],
            heading="Photo",
        ),
        FieldPanel("embassy_logo"),
        FieldPanel("background"),
        FieldPanel("social_media_link"),
        FieldPanel("social_media_text"),
        FieldPanel("address"),
        FieldPanel("telephone"),
        FieldPanel("opening_hours"),
        FieldPanel("closure_dates"),
        FieldPanel("emergency_contact_details"),
        FieldPanel("links"),
        FieldPanel('tags'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        snippet_published.send(sender=self.__class__, instance=self)

    def get_preview_template(self, request, mode_name):
        return "patterns/snippets/peoplesnippet.html"

    @property
    def revisions(self):
        return self._revisions

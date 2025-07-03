# -*- coding: utf-8 -*-
import json

from django.db import models
from django.forms import ValidationError
from django.utils.functional import cached_property
from django.utils.text import slugify

from wagtail.fields import StreamField
from wagtail.admin.panels import TabbedInterface, ObjectList, FieldPanel, MultiFieldPanel, InlinePanel

from irelandie_news.models import NewsPage

from irelandie_utils.models import HeroPage
from irelandie_utils.blocks import FreeFormBlocks, ImageBlock, GenericHeroBlock, HomepageFeatureBlock
from irelandie_tags.models import TagPage
from wagtail.blocks import PageChooserBlock
from irelandie_navigation.blocks import NoticeBarWithMessageLink
from wagtail.images import get_image_model_string

IMAGE_MODEL = get_image_model_string()


class FreeFormPageBase(HeroPage):
    """
    A page model that is free form and has access to all stream blocks.
    """
    five_panel_block = StreamField(
        [
            ("five_panel_block", HomepageFeatureBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    body = StreamField(FreeFormBlocks(), blank=True)

    content_panels = ([FieldPanel("five_panel_block", heading="5 Panel Block")] +
                      HeroPage.content_panels + [
                          FieldPanel("body"),
                      ])

    hero_panel = HeroPage.hero_panel_with_size

    def clean(self):
        super().clean()
        if self.hero_image and self.five_panel_block or self.hero_video and self.five_panel_block:
            raise ValidationError(
                {
                    "five_panel_block": ValidationError(
                        "You can't choose both a five_panel_block and a hero image/video for the hero media. "
                        "Choose a five_panel_block or a hero image/video"
                    ),
                    "hero_image": ValidationError(
                        "You can't choose both a five_panel_block and a hero image/video for the hero media. "
                        "Choose a five_panel_block or a hero image/video"
                    ),
                }
            )

    class Meta:
        abstract = True
        verbose_name = "Free Form Page Base"
        verbose_name_plural = "Free Form Pages Base"


class FreeFormPage(FreeFormPageBase):
    template = "patterns/pages/irelandie_pages/free_form_page.html"
    subtitle = models.TextField(blank=True)
    root_page = models.BooleanField(default=True)
    generic_hero = StreamField(
        [
            ("generic_hero", GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    favicon = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    featured_news = models.BooleanField(default=False)
    twitter_title = models.CharField(max_length=50, blank=True)

    twitter_feed = models.ForeignKey(
        "utils.TwitterEmbed",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )
    notice_bar = StreamField(
        [
            ("noticebar", NoticeBarWithMessageLink()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    tags = StreamField(
        [
            ("tags", PageChooserBlock(required=False, page_type=TagPage))
        ],
        null=True
    )
    default_image = StreamField(
        [
            ("default_image", ImageBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    twitter_url = models.URLField(blank=True, help_text="Full Twitter profile URL")
    facebook_url = models.URLField(blank=True, help_text="Full Facebook page URL")
    youtube_url = models.URLField(blank=True, help_text="Full YouTube channel URL")
    linkedin_url = models.URLField(blank=True, help_text="Full LinkedIn profile URL")
    instagram_url = models.URLField(blank=True, help_text="Full Instagram profile URL")
    weibo_url = models.URLField(blank=True, help_text="Full Weibo profile URL")

    social_media_panels = MultiFieldPanel(
        [
            FieldPanel("twitter_url"),
            FieldPanel("facebook_url"),
            FieldPanel("youtube_url"),
            FieldPanel("linkedin_url"),
            FieldPanel("instagram_url"),
            FieldPanel("weibo_url"),
        ],
        heading="Social Media URLs",
    )
    content_panels = [FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block")] + [
        FieldPanel("subtitle", help_text="Please include a brief description of this page/article. This will not "
                                         "appear live on the page, but will appear publicly as a subtitle in other "
                                         "areas of the site that link to this page.")] + (
                         FreeFormPageBase.content_panels +
                         [
                             FieldPanel("featured_news",
                                        help_text="Checking this box will feature this news item on your "
                                                  "main news page."),
                             MultiFieldPanel([
                                 FieldPanel("notice_bar"),
                             ], heading="Noticebar settings"
                             ),
                             MultiFieldPanel([
                                 FieldPanel("twitter_title"),
                                 FieldPanel("twitter_feed"),
                             ], heading="Twitter feed"),
                             InlinePanel('page_related_tags', label="Related category tags"),
                             InlinePanel('page_related_destination_tags', label="Related destination"),
                         ]
                     )

    settings_panels = (
        [
            FieldPanel("root_page", permission="access_admin"),
            FieldPanel("favicon", permission="access_admin"),
            FieldPanel("default_image", permission="access_admin"),
        ] +
        HeroPage.settings_panels

    )

    promote_panels = FreeFormPageBase.promote_panels + [social_media_panels]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(FreeFormPageBase.hero_panel, heading='Hero'),
        ObjectList(promote_panels, heading='Promote', permission="superuser"),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
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
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'Free Form Page':
                missions = FreeFormPage.objects.live().get(id=p.id)
                if missions.root_page:
                    context['default_image'] = missions.default_image
        return context

    @cached_property
    def related_articles(self):
        return (
            NewsPage.objects
            .descendant_of(self)
            .filter(locale=self.locale,
                    featured_home=True)
            .public()
            .live()
            .order_by("-publication_date")[:4]
            .specific()
        )

    def get_speakable_selectors(self):
        selectors = []
        for idx, block in enumerate(self.body, start=1):
            value = getattr(block, 'value', {})
            slug = slugify(block.block_type)
            if hasattr(value, 'get') and value.get('is_speakable', False):
                selector = f"[data-speakable='{slug}-{idx}']"
                selectors.append(selector)

        return selectors

    @property
    def same_as_links(self):
        return list(filter(None, [
            self.twitter_url,
            self.facebook_url,
            self.youtube_url,
            self.linkedin_url,
            self.instagram_url,
            self.weibo_url,
        ]))

    def get_schema_json(self):
        allowed_paths = [
            "/en/about/",
            "/en/dfa/",
            "/en/irish-aid/",
        ]
        print(self.full_url)

        if self.full_url and any(self.full_url.endswith(path) for path in allowed_paths):
            speakable_selectors = self.get_speakable_selectors()

            schema = {
                "@context": "https://schema.org",
                "@type": "GovernmentOrganization",
                "name": self.title,
                "url": self.full_url,
                "sameAs": self.same_as_links,  # assume this returns list of URLs
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": self.full_url,
                },
            }

            # Add speakable only if selectors exist
            if speakable_selectors:
                schema["mainEntityOfPage"]["speakable"] = {
                    "@type": "SpeakableSpecification",
                    "cssSelector": speakable_selectors
                }

            return json.dumps(schema, indent=2)

        return ""

    def clean(self):
        if (
            self.generic_hero and self.hero_image or self.generic_hero and self.hero_video or
            self.generic_hero and self.five_panel_block and self.hero_image or
            self.generic_hero and self.five_panel_block and self.hero_video or
            self.generic_hero and self.five_panel_block or self.hero_image and self.five_panel_block or
            self.hero_video and self.five_panel_block):
            raise ValidationError(
                {
                    "five_panel_block": ValidationError(
                        "Choose only a five_panel_block or a generic_hero or a hero image/video"
                    ),
                    "generic_hero": ValidationError(
                        "Choose only a five_panel_block or a generic_hero or a hero image/video"
                    ),
                    "hero_image": ValidationError(
                        "Choose only a five_panel_block or a generic_hero or a hero image/video"
                    ),
                }
            )

    def save(self, *args, **kwargs):
        from wagtail.core.signals import page_published
        super().save(*args, **kwargs)
        if self.live:  # Ensure the page is published
            page_published.send(sender=self.__class__, instance=self)

    class Meta:
        verbose_name = "Free Form Page"

# -*- coding: utf-8 -*-
import json

from django.db import models
from django.forms import ValidationError
from django.utils.functional import cached_property

from wagtail.fields import StreamField
from wagtail.admin.panels import TabbedInterface, ObjectList, FieldPanel, MultiFieldPanel, InlinePanel

from irelandie_news.models import NewsPage

from irelandie_utils.models import HeroPage
from irelandie_utils.blocks import FreeFormBlocks, ImageBlock, GenericHeroBlock, HomepageFeatureBlock
from irelandie_tags.models import TagPage
from wagtail.blocks import PageChooserBlock
from irelandie_navigation.blocks import NoticeBarWithMessageLink
from wagtail.images import get_image_model_string
from wagtail_charts.blocks import EXTRA_CHART_COLOUR_CHOICES, ChartBlock

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

    organization_name = models.CharField(
        max_length=255,
        default="Department of Foreign Affairs and Trade",
        blank=True
    )

    organization_description = models.CharField(blank=True, max_length=255)

    organization_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    mainEntityOfPage_name = models.CharField(
        max_length=255,
        blank=True
    )
    mainEntityOfPage_description = models.CharField(blank=True, max_length=255)

    twitter_url = models.URLField(blank=True, help_text="Full X profile URL")
    facebook_url = models.URLField(blank=True, help_text="Full Facebook page URL")
    youtube_url = models.URLField(blank=True, help_text="Full YouTube channel URL")
    linkedin_url = models.URLField(blank=True, help_text="Full LinkedIn profile URL")
    instagram_url = models.URLField(blank=True, help_text="Full Instagram profile URL")
    weibo_url = models.URLField(blank=True, help_text="Full Weibo profile URL")

    social_media_panels = MultiFieldPanel(
        [
            FieldPanel("twitter_url", heading="X url"),
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
                                 FieldPanel("twitter_title", heading="X Title"),
                                 FieldPanel("twitter_feed", heading="X Feed"),
                             ], heading="X feed"),
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

    promote_panels = (FreeFormPageBase.promote_panels +
                      [
                          MultiFieldPanel([
                              FieldPanel("organization_name"),
                              FieldPanel("organization_description"),
                              FieldPanel("organization_logo"),
                          ], heading="Organization Schema Settings"),
                          MultiFieldPanel([
                              FieldPanel("mainEntityOfPage_name"),
                              FieldPanel("mainEntityOfPage_description"),
                          ], heading="mainEntityOfPage")
                      ]
                      + [social_media_panels])

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

    def get_breadcrumb_schema(self):
        ancestors = list(
            self.get_ancestors(inclusive=True).live().filter(depth__gte=2)
        )
        ancestors = ancestors[-6:]

        item_list = []
        for position, ancestor in enumerate(ancestors, start=1):
            item_list.append({
                "@type": "ListItem",
                "position": position,
                "name": ancestor.title,
                "item": ancestor.full_url
            })

        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": item_list
        }

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

    @cached_property
    def has_charts(self) -> bool:
        """Check if the page contains any chart blocks.

        Returns:
            bool: True if the page has chart_block elements in its body StreamField.
        """
        if not hasattr(self, "body"):
            return False

        try:
            return any(block.block_type == "chart_block" for block in self.body)
        except (AttributeError, TypeError):
            return False

    def get_schema_json(self):
        allowed_paths = [
            "/en/about/",
            "/en/dfa/",
            "/en/irish-aid/",
        ]

        if self.full_url and any(self.full_url.endswith(path) for path in allowed_paths):
            main_schema = {
                "@context": "https://schema.org",
                "@type": "GovernmentOrganization",
                "name": self.organization_name,
                "url": self.full_url,
                "parentOrganization": {
                    "@type": "GovernmentOrganization",
                    "name": "Government of Ireland",
                    "url": "https://www.gov.ie",
                },
                "description": self.organization_description or "",
                "logo": self.organization_logo.get_rendition("original").url if self.organization_logo else "",
                "sameAs": self.same_as_links,
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": self.full_url,
                    "name": self.mainEntityOfPage_name,
                    "description": self.mainEntityOfPage_description or "",
                },
            }

            breadcrumb_schema = self.get_breadcrumb_schema()

            return json.dumps([main_schema, breadcrumb_schema], indent=2)

        return ""

    def clean(self):
        if (
            self.generic_hero and self.hero_image or self.generic_hero and self.hero_video or
            self.generic_hero and self.five_panel_block and self.hero_image or
            self.generic_hero and self.five_panel_block and self.hero_video or
            self.generic_hero and self.five_panel_block or self.hero_image and self.five_panel_block or
            self.hero_video and self.five_panel_block
        ):
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

    SCHEMA_FIELDS = [
        "organization_name",
        "organization_description",
        "organization_logo",
        "mainEntityOfPage_name",
        "mainEntityOfPage_description",
        "twitter_url",
        "facebook_url",
        "youtube_url",
        "linkedin_url",
        "instagram_url",
        "weibo_url",
    ]

    def save_revision(self, *args, **kwargs):
        if self.pk:
            old_page = self.__class__.objects.get(pk=self.pk)
            for field in self.SCHEMA_FIELDS:
                if not getattr(self, field):
                    setattr(self, field, getattr(old_page, field))
        return super().save_revision(*args, **kwargs)

    def save(self, *args, **kwargs):
        from wagtail.signals import page_published
        super().save(*args, **kwargs)
        if self.live:  # Ensure the page is published
            page_published.send(sender=self.__class__, instance=self)

    class Meta:
        verbose_name = "Free Form Page"

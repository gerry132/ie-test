# -*- coding: utf-8 -*-
import json
import mimetypes

from django.db import models
from django.utils.formats import date_format
from django.utils.text import slugify
from wagtail.images import get_image_model_string
from wagtailmedia.edit_handlers import MediaChooserPanel

# from wagtailseo.models import SeoMixin, SeoType

from irelandie_utils.models import HeroPage, SocialFields, ListingFields
from irelandie_utils.blocks import GenericHeroBlock
from .blocks import StoryPageBlock
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, InlinePanel, MultiFieldPanel

IMAGE_MODEL = get_image_model_string()


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

    TYPE_CHOICES = [
        ('Person', 'Person'),
        ('Organization', 'Organization'),
    ]

    schema_type = models.CharField(
        max_length=20,
        default="article",
    )

    article_headline = models.CharField(max_length=255, blank=True)
    article_image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose the image you wish to be displayed when this page appears in listings",
    )
    article_description = models.TextField(blank=True)
    article_date_published = models.DateTimeField(null=True, blank=True)
    article_date_modified = models.DateTimeField(null=True, blank=True)
    article_author_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='Organization',
        blank=True
    )
    article_author = models.CharField(
        max_length=255,
        default="Department of Foreign Affairs and Trade",
        blank=True
    )
    article_publisher_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='Organization',
        blank=True
    )
    article_publisher_name = models.CharField(
        max_length=255,
        blank=True
    )
    article_publisher_url = models.URLField(blank=True)
    article_publisher_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose the image you wish to be displayed when this page appears in listings",
    )

    article_audio = models.ForeignKey(
        "wagtailmedia.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    article_video = models.ForeignKey(
        "wagtailmedia.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    # Indicate this is article-style content.
    # seo_content_type = SeoType.ARTICLE

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

    COMMON_PROMOTE_PANELS = (
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
    )

    promote_panels = (
        [
            MultiFieldPanel(COMMON_PROMOTE_PANELS, heading="For search engines"),
            FieldPanel('show_in_menus'),
        ] +
        SocialFields.promote_panels +
        ListingFields.promote_panels
        + [
            FieldPanel('schema_type'),
            MultiFieldPanel(
                [
                    FieldPanel("article_headline", classname="schema-article"),
                    FieldPanel("article_image", classname="schema-article"),
                    FieldPanel("article_description", classname="schema-article"),
                    FieldPanel("article_date_published", classname="schema-article"),
                    FieldPanel("article_date_modified", classname="schema-article"),
                    FieldPanel("article_author_type", classname="schema-article"),
                    FieldPanel("article_author", classname="schema-article"),
                    FieldPanel("article_publisher_type", classname="schema-article"),
                    FieldPanel("article_publisher_name", classname="schema-article"),
                    FieldPanel("article_publisher_url", classname="schema-article"),
                    FieldPanel("article_publisher_logo", classname="schema-article"),
                    MediaChooserPanel("article_audio", media_type="audio", classname="schema-article"),
                    MediaChooserPanel("article_video", media_type="video", classname="schema-article"),
                ],
                heading="Article Schema",
            ),
        ]
    )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel, heading='Hero'),
        ObjectList(promote_panels, heading='Promote'),
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

    def get_speakable_selectors(self):
        selectors = []
        for idx, block in enumerate(self.body, start=1):
            value = getattr(block, 'value', {})
            slug = slugify(block.block_type)
            if hasattr(value, 'get') and value.get('is_speakable', False):
                selector = f"[data-speakable='{slug}-{idx}']"
                selectors.append(selector)

        return selectors

    def get_breadcrumb_schema(self):
        ancestors = list(
            self.get_ancestors(inclusive=True)
            .filter(depth__gte=1)
            .live()
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

    def get_schema_json(self):
        schemas = []
        if self.schema_type == "article":
            article_schema = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": self.article_headline,
                "description": self.article_description,
                "datePublished": self.article_date_published.isoformat() if self.article_date_published else None,
                "dateModified": self.article_date_modified.isoformat() if self.article_date_modified else None,
                "author": {
                    "@type": self.article_author_type,
                    "name": self.article_author,
                },
                "publisher": {
                    "@type": self.article_publisher_type,
                    "name": self.article_publisher_name,
                    "url": self.article_publisher_url,
                },
                "image": self.article_image.get_rendition("original").url if self.article_image else None,
            }
            speakable_selectors = self.get_speakable_selectors()
            if speakable_selectors:
                article_schema["speakable"] = {
                    "@type": "SpeakableSpecification",
                    "cssSelector": speakable_selectors
                }

            if self.article_publisher_logo:
                article_schema["publisher"]["logo"] = {
                    "@type": "ImageObject",
                    "url": self.article_publisher_logo.get_rendition("original").url
                }

            if self.article_audio:
                audio_file = self.article_audio
                article_schema["audio"] = {
                    "@type": "AudioObject",
                    "name": audio_file.title if hasattr(audio_file, 'title') else "Audio",
                    "contentUrl": audio_file.url,
                    "encodingFormat": mimetypes.guess_type(audio_file.url)[0],
                    "uploadDate": date_format(audio_file.created_at, "Y-m-d") if hasattr(audio_file,
                                                                                         "created_at") else None,
                    "duration": audio_file.duration
                }

            if self.article_video:
                video_file = self.article_video
                article_schema["video"] = {
                    "@type": "VideoObject",
                    "contentUrl": video_file.url,
                    "encodingFormat": mimetypes.guess_type(video_file.url)[0],
                    "name": video_file.title if hasattr(video_file, 'title') else "Video",
                    "description": video_file.description if hasattr(video_file, 'description') else "Video content",
                    "thumbnailUrl": video_file.thumbnail.url if hasattr(video_file,
                                                                        'thumbnail') and video_file.thumbnail
                    else "https://example.com/default-thumbnail.jpg",
                    "uploadDate": video_file.created.strftime('%Y-%m-%dT%H:%M:%S%z') if hasattr(video_file,
                                                                                                'created') else
                    "2024-01-01T00:00:00+00:00",
                }

            schemas.append({k: v for k, v in article_schema.items() if v is not None})

        # Add breadcrumb schema
        breadcrumb_schema = self.get_breadcrumb_schema()
        schemas.append(breadcrumb_schema)

        return json.dumps(schemas, indent=2)

    @property
    def schema_json(self):
        return self.get_schema_json()

    def save(self, *args, **kwargs):
        from wagtail.core.signals import page_published
        super().save(*args, **kwargs)
        if self.live:  # Ensure the page is published
            page_published.send(sender=self.__class__, instance=self)

    class Meta:
        verbose_name = "Story page"

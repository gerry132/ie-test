# -*- coding: utf-8 -*-
import mimetypes

from django.db import models
from django.utils.formats import date_format
from wagtail.images import get_image_model_string
from wagtailmedia.edit_handlers import MediaChooserPanel

# from wagtailseo.models import SeoMixin, SeoType
import json
from irelandie_utils.models import HeroPage, SocialFields, ListingFields
from irelandie_utils.blocks import GenericHeroBlock
from irelandie_parallax.blocks import ParallaxAdvancedRichTextBlock, ParallaxImageVideoBlock, \
    ParallaxLogoCardsBlock, ParallaxStoryPhotoGalleryBlock, ParallaxTimelinePhotoGalleryBlock, ParallaxLinkCardsBlock, \
    ParallaxYoutubeVimeoBlock, DoubleFeature, ParallaxHTMLBlock
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, MultiFieldPanel, InlinePanel

IMAGE_MODEL = get_image_model_string()


class Parallax(HeroPage):
    template = "patterns/pages/irelandie_story/parallax_page.html"
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

    body = StreamField(
        [
            ("ParallaxAdvancedRichTextBlock", ParallaxAdvancedRichTextBlock()),
            ("ParallaxImageVideoBlock", ParallaxImageVideoBlock()),
            ("ParallaxYoutubeVimeoBlock", ParallaxYoutubeVimeoBlock()),
            ("ParallaxHTMLBlock", ParallaxHTMLBlock()),
            ("ParallaxLogocards", ParallaxLogoCardsBlock()),
            ("ParallaxStoryPhotoGalleryBlock", ParallaxStoryPhotoGalleryBlock()),
            ("ParallaxTimelinePhotoGalleryBlock", ParallaxTimelinePhotoGalleryBlock()),
            ("ParallaxLinkCardsBlock", ParallaxLinkCardsBlock()),
            ("DoubleFeature", DoubleFeature()),

        ],
        blank=True,
        null=True,
    )

    SCHEMA_TYPE_CHOICES = [
        ("article", "Article"),
        ("event", "Event"),
    ]

    TYPE_CHOICES = [
        ('Person', 'Person'),
        ('Organization', 'Organization'),
    ]

    schema_type = models.CharField(
        max_length=20,
        choices=SCHEMA_TYPE_CHOICES,
        default="article",
        help_text="Choose schema type for this page"
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

    EVENT_ATTENDANCE_MODES = [
        ('OfflineEventAttendanceMode', 'Offline'),
        ('OnlineEventAttendanceMode', 'Online'),
        ('MixedEventAttendanceMode', 'Mixed'),
    ]

    EVENT_STATUS_CHOICES = [
        ('EventScheduled', 'Scheduled'),
        ('EventCancelled', 'Cancelled'),
        ('EventPostponed', 'Postponed'),
        ('EventMovedOnline', 'Moved Online'),
    ]

    LOCATION_TYPE_CHOICES = [
        ('Place', 'Place'),
        ('Postal address', 'Postal address'),
    ]

    event_name = models.CharField(max_length=255, blank=True)
    event_start_date = models.DateField(null=True, blank=True)
    event_end_date = models.DateField(null=True, blank=True)
    event_attendance_mode = models.CharField(
        max_length=30,
        choices=EVENT_ATTENDANCE_MODES,
        default='OfflineEventAttendanceMode'
    )
    event_status = models.CharField(
        max_length=30,
        choices=EVENT_STATUS_CHOICES,
        default='EventScheduled'
    )

    event_location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default='Place',
        help_text="Type of location"
    )

    # Location fields (for Place type)
    event_place_name = models.CharField(max_length=255, blank=True)
    event_place_address = models.CharField(max_length=255, blank=True)
    event_street_address = models.CharField(max_length=255, blank=True)
    event_address_locality = models.CharField(max_length=255, blank=True)
    event_postal_code = models.CharField(max_length=20, blank=True)
    event_address_country = models.CharField(max_length=255, blank=True)

    event_description = models.TextField(blank=True)
    event_image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    event_organizer_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='Organization',
        blank=True
    )
    event_organizer_name = models.CharField(
        max_length=255,
        blank=True
    )
    event_organizer_url = models.URLField(blank=True)
    event_performer = models.CharField(max_length=255, blank=True)

    content_panels = HeroPage.content_panels + [
        FieldPanel("subtitle", help_text="Please include a brief description of this page/article. This will not "
                                         "appear live on the page, but will appear publicly as a subtitle in other "
                                         "areas of the site that link to this page."),
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
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

            MultiFieldPanel(
                [
                    FieldPanel("event_name", classname="schema-event"),
                    FieldPanel("event_start_date", classname="schema-event"),
                    FieldPanel("event_end_date", classname="schema-event"),
                    FieldPanel("event_attendance_mode", classname="schema-event"),
                    FieldPanel("event_status", classname="schema-event"),
                    FieldPanel("event_location_type", classname="schema-event"),
                    FieldPanel("event_place_name", classname="schema-event"),
                    FieldPanel("event_place_address", classname="schema-event"),
                    FieldPanel("event_street_address", classname="schema-event"),
                    FieldPanel("event_address_locality", classname="schema-event"),
                    FieldPanel("event_postal_code", classname="schema-event"),
                    FieldPanel("event_address_country", classname="schema-event"),
                    FieldPanel("event_description", classname="schema-event"),
                    FieldPanel("event_image", classname="schema-event"),
                    FieldPanel("event_organizer_type", classname="schema-event"),
                    FieldPanel("event_organizer_name", classname="schema-event"),
                    FieldPanel("event_organizer_url", classname="schema-event"),
                    FieldPanel("event_performer", classname="schema-event"),
                ],
                heading="Event Schema",
            ),
        ]
    )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel_with_size, heading='Hero'),
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

        elif self.schema_type == "event":
            event_schema = {
                "@context": "https://schema.org",
                "@type": "Event",
                "name": self.event_name,
                "startDate": self.event_start_date.isoformat() if self.event_start_date else None,
                "endDate": self.event_end_date.isoformat() if self.event_end_date else None,
                "eventAttendanceMode": f"https://schema.org/{self.event_attendance_mode}",
                "eventStatus": f"https://schema.org/{self.event_status}",
                "description": self.event_description,
                "performer": {
                    "@type": "PerformingGroup",
                    "name": self.event_performer,
                } if self.event_performer else None,
                "organizer": {
                    "@type": self.event_organizer_type,
                    "name": self.event_organizer_name,
                    "url": self.event_organizer_url
                },
                "image": self.event_image.get_rendition("original").url if self.event_image else None,
            }

            if self.event_location_type == "Place":
                event_schema["location"] = {
                    "@type": "Place",
                    "name": self.event_place_name,
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": self.event_street_address,
                        "addressLocality": self.event_address_locality,
                        "postalCode": self.event_postal_code,
                        "addressCountry": self.event_address_country,
                    }
                }
            schemas.append({k: v for k, v in event_schema.items() if v is not None})

        # Add breadcrumb schema
        breadcrumb_schema = self.get_breadcrumb_schema()
        schemas.append(breadcrumb_schema)

        return json.dumps(schemas, indent=2)

    @property
    def schema_json(self):
        return self.get_schema_json()

    class Meta:
        verbose_name = "Parallax page"

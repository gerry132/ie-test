# -*- coding: utf-8 -*-
from functools import cached_property

from django.db import models
# from wagtailseo.models import SeoMixin

from irelandie_utils.models import BasePage, SocialFields, ListingFields
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, MultiFieldPanel, HelpPanel, InlinePanel
from wagtailmedia.edit_handlers import MediaChooserPanel
from django.core.exceptions import ValidationError
from wagtail.images import get_image_model_string
from wagtail.fields import RichTextField, StreamField
import re
from irelandie_utils import blocks
from wagtail.models import Page
from irelandie_utils.constants import USAStates

IMAGE_MODEL = get_image_model_string()
ALT_HELP_TEXT = """A short one-sentence literal description
                    of the %s is
                    required to make the page accessible to the
                    visually impaired. Details: https://axesslab.com/alt-texts/"""

ALT_VID = ALT_HELP_TEXT % 'video'
ALT_IMAGE = ALT_HELP_TEXT % 'image'


class ListingsContents(models.Model):
    CHOICES = [("", "Choose an icon (optional)"),
               ("art-easel", "Art Easel"),
               ("art-palette", "Art Palette"),
               ("classical-music", "Classical Music"),
               ("culture", "Culture"),
               ("dance", "Dance"),
               ("fashion", "Fashion"),
               ("film", "Film"),
               ("film-2", "Film 2"),
               ("gallery-exhibition", "Gallery Exhibition"),
               ("literature", "Literature"),
               ("microphone", "Microphone"),
               ("museum", "Museum"),
               ("music", "Music"),
               ("music-2", "Music 2"),
               ("photography", "Photography"),
               ("screening-play", "Screening Play"),
               ("sculpture", "Sculpture"),
               ("speech-talk", "Speech Talk"),
               ("spoken-word", "Spoken Word"),
               ("stand-up", "Stand Up"),
               ("theatre", "Theatre"),
               ("tickets", "Tickets"),
               ]
    icon = models.CharField(
        max_length=20, choices=CHOICES, blank=True, default="Choose an icon (optional)"
    )
    image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_alt = models.CharField(
        max_length=255,
        blank=True,
        help_text=ALT_IMAGE
    )
    event_title = models.CharField(max_length=60, help_text="60 character limit")
    event_link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    event_link_url = models.URLField(blank=True, help_text="An external link.")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField()
    venue = models.CharField(max_length=100, blank=True, help_text="100 character limit")
    event_details = RichTextField(features=["bold", "italic", "link"],
                                  blank=True, null=True, max_length=200, help_text="150 character limit")

    class Meta:
        abstract = True


class ListingsContentPage(ListingsContents, BasePage):
    template = "patterns/pages/irelandie_listings/listings_content_page.html"
    location = models.TextField(blank=True)

    def clean(self):
        if self.start_date and self.end_date < self.start_date:
            raise ValidationError(
                {
                    "end_date": ValidationError(
                        "End date should be greater than start date."
                    ),
                }
            )

        if self.event_link_page and self.event_link_url:
            raise ValidationError(
                {
                    "event_link_page": ValidationError(
                        "You must specify event_link_page or event_link_url. You can't use both."
                    ),
                    "event_link_url": ValidationError(
                        "You must specify link event_link_page or event_link_url. You can't use both."
                    ),
                }
            )
        if not self.icon and not self.image:
            raise ValidationError(
                {
                    "icon": ValidationError(
                        "You must specify icon or image."
                    ),
                    "image": ValidationError(
                        "You must specify icon or image."
                    ),
                }
            )

        if self.icon and self.image:
            raise ValidationError(
                {
                    "icon": ValidationError(
                        "You must specify icon or image. You can't use both."
                    ),
                    "image": ValidationError(
                        "You must specify link icon or image. You can't use both."
                    ),
                }
            )
        if self.image and not self.image_alt:
            raise ValidationError(
                {
                    "image_alt": ValidationError(
                        "You must specify image_alt if you choose the image."
                    ),
                }
            )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('image'),
                FieldPanel("image_alt"),
                FieldPanel('icon'),
            ],
            heading="Image/Icon"
        ),
        MultiFieldPanel(
            [
                FieldPanel('event_title'),
                FieldPanel('event_link_page'),
                FieldPanel('event_link_url'),
            ],
            heading="Event Title"
        ),
        MultiFieldPanel(
            [
                HelpPanel("If your event runs across a date range, add a start and end date. If your event runs on "
                          "one specified day, only enter an end date."),
                FieldPanel('start_date'),
                FieldPanel('end_date'),
            ],
            heading="Event Date"
        ),
        FieldPanel('venue'),
        FieldPanel('location'),
        FieldPanel('event_details'),
    ]
    settings_panels = Page.settings_panels + ([
                                                  MultiFieldPanel(
                                                      [
                                                          FieldPanel("custom_header", permission="access_admin"),
                                                          FieldPanel("custom_footer", permission="access_admin")
                                                      ],
                                                      "Root Navigation"
                                                  ),
                                              ] +
                                              BasePage.webchat_panel
                                              )
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
    )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])

    class Meta:
        verbose_name = "Listings Content"

    search_fields = []

    def get_indexed_instance(self):
        return None


class ListingsContentUSAPage(ListingsContents, BasePage):
    template = "patterns/pages/irelandie_listings/listings_content_page.html"

    city = models.TextField(blank=True)
    state = models.CharField(
        max_length=4, choices=USAStates.choices, blank=True, default=USAStates.CHOOSE_A_STATE
    )

    def clean(self):
        if self.start_date and self.end_date < self.start_date:
            raise ValidationError(
                {
                    "end_date": ValidationError(
                        "End date should be greater than start date."
                    ),
                }
            )

        if self.event_link_page and self.event_link_url:
            raise ValidationError(
                {
                    "event_link_page": ValidationError(
                        "You must specify event_link_page or event_link_url. You can't use both."
                    ),
                    "event_link_url": ValidationError(
                        "You must specify link event_link_page or event_link_url. You can't use both."
                    ),
                }
            )
        if not self.icon and not self.image:
            raise ValidationError(
                {
                    "icon": ValidationError(
                        "You must specify icon or image."
                    ),
                    "image": ValidationError(
                        "You must specify icon or image."
                    ),
                }
            )

        if self.icon and self.image:
            raise ValidationError(
                {
                    "icon": ValidationError(
                        "You must specify icon or image. You can't use both."
                    ),
                    "image": ValidationError(
                        "You must specify link icon or image. You can't use both."
                    ),
                }
            )
        if self.image and not self.image_alt:
            raise ValidationError(
                {
                    "image_alt": ValidationError(
                        "You must specify image_alt if you choose the image."
                    ),
                }
            )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('image'),
                FieldPanel("image_alt"),
                FieldPanel('icon'),
            ],
            heading="Image/Icon"
        ),
        MultiFieldPanel(
            [
                FieldPanel('event_title'),
                FieldPanel('event_link_page'),
                FieldPanel('event_link_url'),
            ],
            heading="Event Title"
        ),
        MultiFieldPanel(
            [
                HelpPanel("If your event runs across a date range, add a start and end date. If your event runs on "
                          "one specified day, only enter an end date."),
                FieldPanel('start_date'),
                FieldPanel('end_date'),
            ],
            heading="Event Date"
        ),
        FieldPanel('venue'),
        MultiFieldPanel(
            [
                FieldPanel('city'),
                FieldPanel('state'),
            ],
            heading="Location"
        ),
        FieldPanel('event_details'),
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
    )

    settings_panels = Page.settings_panels + ([
                                                  MultiFieldPanel(
                                                      [
                                                          FieldPanel("custom_header", permission="access_admin"),
                                                          FieldPanel("custom_footer", permission="access_admin")
                                                      ],
                                                      "Root Navigation"
                                                  ),
                                              ] +
                                              BasePage.webchat_panel
                                              )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])

    class Meta:
        verbose_name = "Listings Content USA"

    search_fields = []

    def get_indexed_instance(self):
        return None


class ListingsFeaturedPage(BasePage):
    max_count_per_parent = 1
    template = "patterns/pages/irelandie_listings/listings_featured_page.html"

    image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_alt = models.CharField(
        max_length=255,
        blank=True,
        help_text=ALT_IMAGE
    )
    youtube_or_vimeo_embed = models.CharField(max_length=255, null=True, blank=True)
    video = models.ForeignKey(
        "wagtailmedia.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    video_alt = models.CharField(blank=True,
                                 null=True,
                                 max_length=255,
                                 help_text=ALT_VID)
    event_title = models.CharField(max_length=60, help_text="60 character limit")
    event_link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    event_link_url = models.URLField(blank=True, help_text="An external link.")
    event_details = RichTextField(features=["bold", "italic", "link"],
                                  blank=True, null=True, max_length=200, help_text="200 character limit")

    def clean(self):

        if self.event_link_page and self.event_link_url:
            raise ValidationError(
                {
                    "event_link_page": ValidationError(
                        "You must specify event_link_page or event_link_url. You can't use both."
                    ),
                    "event_link_url": ValidationError(
                        "You must specify link event_link_page or event_link_url. You can't use both."
                    ),
                }
            )
        if not self.video and not self.image and not self.youtube_or_vimeo_embed:
            raise ValidationError(
                {
                    "video": ValidationError(
                        "You must specify image or video or youtube_or_vimeo_embed."
                    ),
                    "image": ValidationError(
                        "You must specify image or video or youtube_or_vimeo_embed."
                    ),
                    "youtube_or_vimeo_embed": ValidationError(
                        "You must specify image or video or youtube_or_vimeo_embed."
                    ),
                }
            )

        if self.video and self.image:
            raise ValidationError(
                {
                    "video": ValidationError(
                        "You must specify video or image. You can't use both."
                    ),
                    "image": ValidationError(
                        "You must specify video or image. You can't use both."
                    ),
                }
            )
        if self.youtube_or_vimeo_embed and self.image:
            raise ValidationError(
                {
                    "youtube_or_vimeo_embed": ValidationError(
                        "You must specify youtube_or_vimeo_embed or image. You can't use both."
                    ),
                    "image": ValidationError(
                        "You must specify youtube_or_vimeo_embed or image. You can't use both."
                    ),
                }
            )
        if self.image and not self.image_alt:
            raise ValidationError(
                {
                    "image_alt": ValidationError(
                        "You must specify image_alt if you choose the image."
                    ),
                }
            )

        if self.video and not self.video_alt:
            raise ValidationError(
                {
                    "video_alt": ValidationError(
                        "You must specify image_alt if you choose the image."
                    ),
                }
            )

        if self.video and self.youtube_or_vimeo_embed:
            raise ValidationError(
                {
                    "video": ValidationError(
                        "You must specify video or youtube_or_vimeo_embed. You can't use both."
                    ),
                    "youtube_or_vimeo_embed": ValidationError(
                        "You must specify video or youtube_or_vimeo_embed. You can't use both."
                    ),
                }
            )

    def embedding_url(self):

        url = self.youtube_or_vimeo_embed
        if url is None:
            return None
        if "/embed/" in url:
            return url
        if 'youtube.com' in url or 'youtu.be' in url:
            pattern = r"^(http(s)?:\/\/)?(www\.)?((youtu)(be)?)?"
            pattern += r"(\.(com)|\.(be))?(\/)(watch\?v=)?|(\&.+)?"

            video_id = re.sub(pattern, "", url)
            video_id = re.sub(r"(&list.+)|((\s)$)", "", video_id)

            return f"https://www.youtube.com/embed/{video_id}"
        if 'vimeo.com' in url:
            embed_url = url.replace('vimeo.com', 'player.vimeo.com/video')
            embed_url_with_parameters = embed_url
            return embed_url_with_parameters
        else:
            return None

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('image'),
                FieldPanel("image_alt"),
                FieldPanel('youtube_or_vimeo_embed'),
                MediaChooserPanel('video'),
                FieldPanel("video_alt"),
            ],
            heading="Image/Video"
        ),
        MultiFieldPanel(
            [
                FieldPanel('event_title'),
                FieldPanel('event_link_page'),
                FieldPanel('event_link_url'),
            ],
            heading="Event Title"
        ),
        FieldPanel('event_details'),
    ]
    settings_panels = Page.settings_panels + ([
                                                  MultiFieldPanel(
                                                      [
                                                          FieldPanel("custom_header", permission="access_admin"),
                                                          FieldPanel("custom_footer", permission="access_admin")
                                                      ],
                                                      "Root Navigation"
                                                  ),
                                              ] +
                                              BasePage.webchat_panel
                                              )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(BasePage.promote_panels, heading='Promote', permission="superuser"),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])

    class Meta:
        verbose_name = "Listings Featured"

    search_fields = []

    def get_indexed_instance(self):
        return None


class ListingsPageIndex(BasePage):
    template = "patterns/pages/irelandie_listings/listings_index_page.html"
    subpage_types = [
        'ListingsContentPage',
        'ListingsFeaturedPage'
    ]
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    advanced_rich_text = StreamField(
        [
            ("advanced_rich_text", blocks.AdvancedRichTextBlock()),
        ],
        blank=True,
        null=True,
    )
    advanced_rich_text_and_logo_cards = StreamField(
        [
            (
                "rich_text_advanced",
                blocks.AdvancedRichTextBlock(),
            ),
            (
                "logo_cards",
                blocks.LogoCardsBlock()
            ),
        ],
        blank=True,
        null=True,
    )

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
        context['listings_featured_page'] = (
            ListingsFeaturedPage.objects.child_of(self)
            .public()
            .live()
            .specific()
        )
        from django.db.models import Case, When, DateField
        context['listings_contents_page'] = ListingsContentPage.objects.child_of(self).public().live().annotate(
            testing=Case(When(start_date__isnull=False, then='start_date'), default='end_date',
                         output_field=DateField())).order_by('testing').specific()

        return context

    content_panels = Page.content_panels + [
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("advanced_rich_text"),
        FieldPanel("advanced_rich_text_and_logo_cards"),
        InlinePanel('page_related_tags', label="Related category tags"),
        InlinePanel('page_related_destination_tags', label="Related destination"),
    ]

    def save(self, *args, **kwargs):
        from wagtail.core.signals import page_published
        super().save(*args, **kwargs)
        if self.live:  # Ensure the page is published
            page_published.send(sender=self.__class__, instance=self)

    class Meta:
        verbose_name = "Listings Index"


class ListingsPageUSAIndex(BasePage):
    template = "patterns/pages/irelandie_listings/listings_index_usa.html"
    ajax_template = "patterns/pages/irelandie_listings/ajax_listings_index_usa.html"
    subpage_types = [
        'ListingsContentUSAPage',
        'ListingsFeaturedPage'
    ]
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    advanced_rich_text = StreamField(
        [
            ("advanced_rich_text", blocks.AdvancedRichTextBlock()),
        ],
        blank=True,
        null=True,
    )
    advanced_rich_text_and_logo_cards = StreamField(
        [
            (
                "rich_text_advanced",
                blocks.AdvancedRichTextBlock(),
            ),
            (
                "logo_cards",
                blocks.LogoCardsBlock()
            ),
        ],
        blank=True,
        null=True,
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from django.db.models import Case, When, DateField
        state = None
        city = None
        if request.GET.get('state'):
            if request.GET.get('state') == 'state':
                state = None
            else:
                state = request.GET.get('state')

        elif 'state' in request.GET:
            if request.GET['state']:
                state = request.GET['state']
            else:
                state = None
        elif request.GET.get('city'):
            if request.GET.get('city') == 'city':
                city = None
            else:
                city = request.GET.get('city')

        elif 'city' in request.GET:
            if request.GET['city']:
                city = request.GET['city']
            else:
                city = None
        if state:
            rel_art = (
                ListingsContentUSAPage.objects.child_of(self).public().live().filter(state=state,
                                                                                     locale=self.locale).annotate(
                    testing=Case(When(start_date__isnull=False, then='start_date'), default='end_date',
                                 output_field=DateField())).order_by('testing').specific()
            )
        elif city:
            rel_art = (
                ListingsContentUSAPage.objects.child_of(self).public().live().filter(city=city,
                                                                                     locale=self.locale).annotate(
                    testing=Case(When(start_date__isnull=False, then='start_date'), default='end_date',
                                 output_field=DateField())).order_by('testing').specific()
            )
        else:
            rel_art = (
                ListingsContentUSAPage.objects.child_of(self).public().live().annotate(
                    testing=Case(When(start_date__isnull=False, then='start_date'), default='end_date',
                                 output_field=DateField())).order_by('testing').specific()
            )
        from irelandie_utils.templatetags.util_tags import get_tag_links
        from irelandie_utils.templatetags.util_tags import get_destination_tag_links
        destination_tags = self.related_destination_tags
        context["destination_tag_links"] = get_destination_tag_links(destination_tags)
        tag = self.related_tags
        tagging_links = get_tag_links(tag, self)[0]
        tags_no_links = get_tag_links(tag, self)[1]
        context["tagging_links"] = tagging_links
        context["tags_no_links"] = tags_no_links
        context['listings_featured_page'] = (
            ListingsFeaturedPage.objects.child_of(self)
            .public()
            .live()
            .specific()
        )
        context['listings_contents_page'] = rel_art

        return context

    @cached_property
    def get_state(self):
        stateset = (ListingsContentUSAPage.objects.child_of(self)
                    .public()
                    .live()
                    .values('state')
                    .distinct()
                    )
        state_list = []
        for state in stateset:
            if state['state'] not in state_list and state['state'] != '':
                state_list.append(state['state'])
        return state_list

    @cached_property
    def get_city(self):
        cityset = (ListingsContentUSAPage.objects.child_of(self)
                   .public()
                   .live()
                   .values('city')
                   .distinct()
                   )
        city_list = []
        for state in cityset:
            if state['city'] not in city_list and state['city'] != '':
                city_list.append(state['city'])
        return city_list

    content_panels = Page.content_panels + [
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("advanced_rich_text"),
        FieldPanel("advanced_rich_text_and_logo_cards"),
        InlinePanel('page_related_tags', label="Related category tags"),
        InlinePanel('page_related_destination_tags', label="Related destination"),
    ]

    def save(self, *args, **kwargs):
        from wagtail.core.signals import page_published
        super().save(*args, **kwargs)
        if self.live:  # Ensure the page is published
            page_published.send(sender=self.__class__, instance=self)

    class Meta:
        verbose_name = "Listings Index USA"

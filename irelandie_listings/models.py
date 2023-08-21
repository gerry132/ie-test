# -*- coding: utf-8 -*-
from django.db import models
from irelandie_utils.models import BasePage
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, MultiFieldPanel, HelpPanel
from django.core.exceptions import ValidationError
from wagtail.images import get_image_model_string
from django.utils.translation import gettext_lazy as _
from wagtail.fields import RichTextField

IMAGE_MODEL = get_image_model_string()


class ListingsContentPage(BasePage):
    template = "patterns/pages/irelandie_listings/listings_content_page.html"
    CHOICES = [("", "Choose an icon (optional)"),
               ]
    icon = models.CharField(
        max_length=16, choices=CHOICES, blank=True, default="Choose an icon (optional)"
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
        verbose_name=_("Image Alt text"),
        help_text=_("The alt text shown for accessibility: https://axesslab.com/alt-texts/")
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
    location = models.TextField(blank=True)
    event_details = RichTextField(features=["bold", "italic", "link"],
                                  blank=True, null=True, max_length=150, help_text="150 character limit")

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
        FieldPanel('expire_at',
                   help_text="The date set here will set the expiry for this "
                             "listing. It will be removed from the main listing "
                             "page/list and from public view once expired."),
        FieldPanel('venue'),
        FieldPanel('location'),
        FieldPanel('event_details'),
    ]
    settings_panels = ([
                           FieldPanel('go_live_at'),
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
        ObjectList(BasePage.promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])

    search_fields = []

    def get_indexed_instance(self):
        return None

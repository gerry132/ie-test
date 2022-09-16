# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface, StreamFieldPanel,
)
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractFormField,
    FormBuilder,
    AbstractFormSubmission,
)
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail_honeypot.models import HoneypotMixin

from irelandie_utils.models import BasePage


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", related_name="form_fields")

    CHOICES = FORM_FIELD_CHOICES + (
        ("dateinput", _("Date Input (HTML 5)")),
        ("dateinputlocal", _("Date/Time Input (HTML 5)")),
    )

    field_type = models.CharField(
        verbose_name="field_type",
        max_length=16,
        choices=CHOICES,
    )


class CustomFormBuilder(FormBuilder):
    def create_dateinput_field(self, field, options):
        options["widget"] = forms.DateInput(attrs={"type": "date"})
        return forms.CharField(**options)

    def create_dateinputlocal_field(self, field, options):
        options["widget"] = forms.DateInput(attrs={"type": "datetime-local"})
        return forms.CharField(**options)


class NeverSaveFormSubmission(AbstractFormSubmission):
    def save(self, *args, **kwargs):
        pass


# Never cache form pages since they include CSRF tokens.
@method_decorator(never_cache, name="serve")
class FormPage(HoneypotMixin, BasePage):
    template = "patterns/pages/forms/form_page.html"
    landing_page_template = "patterns/pages/forms/form_page_landing.html"

    introduction = RichTextField(blank=True)
    thank_you_text = RichTextField(
        blank=True,
        help_text="Text displayed to the user on successful submission of the form",
    )
    action_text = models.CharField(
        max_length=32, blank=True, help_text='Form action text. Defaults to "Submit"'
    )

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]
    accordions = models.ForeignKey(
        'utils.Accordion',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("action_text"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
        StreamFieldPanel("accordions"),
    ]

    form_builder = CustomFormBuilder
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(HoneypotMixin.honeypot_panels, heading="Honeypot"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(
                BasePage.settings_panels, heading="Settings", classname="settings"
            ),
        ]
    )

    def get_submission_class(self):
        return NeverSaveFormSubmission

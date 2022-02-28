from django import forms
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractFormField,
    FormBuilder,
)
from wagtail.core.fields import RichTextField
from wagtail.search import index
from wagtailcaptcha.models import WagtailCaptchaEmailForm

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


# Never cache form pages since they include CSRF tokens.
@method_decorator(never_cache, name="serve")
class FormPage(WagtailCaptchaEmailForm, BasePage):
    template = "patterns/pages/forms/form_page.html"
    landing_page_template = "patterns/pages/forms/form_page_landing.html"

    subpage_types = []

    introduction = models.TextField(blank=True)
    thank_you_text = RichTextField(
        blank=True,
        help_text="Text displayed to the user on successful submission of the form",
    )
    action_text = models.CharField(
        max_length=32, blank=True, help_text='Form action text. Defaults to "Submit"'
    )

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

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
    ]

    form_builder = CustomFormBuilder

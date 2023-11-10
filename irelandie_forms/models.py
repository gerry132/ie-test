# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.template.response import TemplateResponse
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)

from datetime import date
from wagtail.admin.mail import send_mail
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractFormField,
    AbstractFormSubmission,
)
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.search import index
from wagtail_honeypot.models import HoneypotMixin
from irelandie_utils.blocks import AdvancedRichTextBlock, AccordionBlock
from irelandie_utils.models import BasePage
from irelandie_utils.utils import get_model_info

from wagtailcaptcha.forms import WagtailCaptchaFormBuilder


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


class CustomMultilineField(forms.CharField):
    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length', 251)
        super().__init__(*args, **kwargs)
        self.widget.attrs['maxlength'] = max_length
        self.widget.attrs['oninput'] = 'validateTextarea(this)'
        self.max_length = max_length


class CustomFormBuilder(WagtailCaptchaFormBuilder):
    def create_multiline_field(self, field, options):
        return CustomMultilineField(widget=forms.Textarea, **options)

    def create_dateinput_field(self, field, options):
        options["widget"] = forms.DateInput(attrs={"type": "date"})
        return forms.CharField(**options)

    def create_dateinputlocal_field(self, field, options):
        options["widget"] = forms.DateInput(attrs={"type": "datetime-local"})
        return forms.CharField(**options)


class NeverSaveFormSubmission(AbstractFormSubmission):
    def save(self, *args, **kwargs):
        pass


class EmailMapBlock(blocks.StructBlock):
    description = blocks.CharBlock(required=True)
    subject = blocks.CharBlock(required=False)
    email = blocks.CharBlock(required=True)


# Never cache form pages since they include CSRF tokens.
@method_decorator(never_cache, name="serve")
class FormPage(HoneypotMixin, BasePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.topic = None
        self.form = None

    template = "patterns/pages/forms/form_page.html"
    landing_page_template = "patterns/pages/forms/form_page_landing.html"

    introduction = StreamField(
        [("rich_text", AdvancedRichTextBlock(blank=True))],
        blank=False,
        null=True,
        min_num=1,
    )
    thank_you_text = RichTextField(
        blank=True,
        help_text="Text displayed to the user on successful submission of the form",
    )
    action_text = models.CharField(
        max_length=32, blank=True, help_text='Form action text. Defaults to "Submit"'
    )
    email_map_text = models.CharField(
        max_length=32, blank=True, help_text='Topic selection for email_map. Defaults to "Choose Topic"'
    )
    email_map = StreamField(
        [("email_map", EmailMapBlock())],
        blank=False,
        null=True,
        help_text="Multiple emails must be in a comma seperated list."
    )
    search_fields = BasePage.search_fields + [index.SearchField("introduction")]
    body = StreamField(
        [("rich_text", AdvancedRichTextBlock(blank=True)),
         ("accordions", AccordionBlock())],
        blank=True,
        null=True,
    )
    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("email_map_text"),
        FieldPanel("email_map"),
        MultiFieldPanel([
            FieldPanel("action_text"),
            FieldPanel("thank_you_text"),
            FieldPanel("from_address", classname="col6"),
            FieldPanel("to_address", classname="col6"),
            FieldPanel("subject"),
        ], heading='Contact Form'),
        FieldPanel("body"),
    ]

    honeypot_panels = [
        MultiFieldPanel(
            [
                FieldPanel("honeypot", permission="access_admin"),
            ],
            heading="Reduce Form Spam",
        )
    ]

    form_builder = CustomFormBuilder
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(honeypot_panels, heading="Honeypot"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(
                BasePage.settings_panels, heading="Settings", classname="settings"
            ),
        ]
    )

    def get_mapped_value(self, topic, item_type='email'):
        for p in self.email_map:
            if p.value.get('description') == topic:
                return p.value.get(item_type)

    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            form = self.get_form(
                request.POST, request.FILES, page=self, user=request.user
            )

            if form.is_valid():
                form_submission = self.process_form_submission(form)
                self.form = form
                return self.render_landing_page(
                    request, form_submission, *args, **kwargs
                )
            else:
                context = self.get_context(request)
                context["form"] = form
                context["form_errors"] = form.errors
                return TemplateResponse(request, self.get_template(request), context)
        else:
            form = self.get_form(page=self, user=request.user)

        context = self.get_context(request)
        context["form"] = form
        return TemplateResponse(request, self.get_template(request), context)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = get_model_info(p.content_type.name, p.id)
                if missions.root_page:
                    context['mission_web_bot'] = missions.web_bot_script
        if request.POST and self.form:
            form = self.form
            form.data = form.data.copy()
            print(form.data)
            del form.data['g-recaptcha-response']

            if form.is_valid():
                subject_item = None
                submitted_date_str = date.today().strftime('%x')
                subject = f"{self.subject} - {submitted_date_str}"
                if 'topic' in request.POST:
                    self.topic = request.POST['topic']
                    addresses = [x.strip() for x in self.get_mapped_value(self.topic).split(',')]
                    subject_item = self.get_mapped_value(self.topic, 'subject')
                else:
                    addresses = [x.strip() for x in self.to_address.split(',')]

                if subject_item:
                    subject = subject_item
                print(self.form.data)

                print(form.data)
                send_mail(subject, self.render_email(form), addresses, self.from_address, )
        return context

    def get_submission_class(self):
        return NeverSaveFormSubmission

    def send_mail(self, form, submit=False):
        self.form = form

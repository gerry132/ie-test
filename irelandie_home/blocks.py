# -*- coding: utf-8 -*-
from django.forms.utils import ErrorList

from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError


class SecondaryCallToAction(blocks.StructBlock):
    """
    A secondary call to action block.
    """

    message = blocks.CharBlock()
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(required=False)

    class Meta:
        icon = 'link'
        template = 'patterns/molecules/streamfield/blocks/secondary_call_to_action.html'
        label = 'Secondary Call To Action'

    def clean(self, value):
        errors = {}
        values = [value["page"], value["url"]]
        # Set only a Page OR a URL
        if all(values):
            message = "Please choose only a page or set a URL."

            errors["page"] = ErrorList([message])
            errors["url"] = ErrorList([message])

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        if value["page"]:
            context["link_url"] = value["page"].url
        elif value["url"]:
            context["link_url"] = value["url"]

        return context

from django import template
from django.utils.translation import pgettext

register = template.Library()


@register.simple_tag
def context_trans(context, message):
    """
    Small helper function to override
    translation with a specific context in
    .po files.
    """
    return pgettext(context, message)

# -*- coding: utf-8 -*-
from django import template
from django.utils.text import camel_case_to_spaces, slugify

from irelandie_utils.models import SocialMediaSettings

import re

register = template.Library()


# Social text
@register.filter(name="social_text")
def social_text(page, site):
    try:
        return page.social_text
    except AttributeError:
        return SocialMediaSettings.for_site(site).default_sharing_text


# Get widget type of a field
@register.filter(name="widget_type")
def widget_type(bound_field):
    return slugify(camel_case_to_spaces(bound_field.field.widget.__class__.__name__))


@register.filter
def next(list_val, current_index):
    """
    Returns the next element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return list_val[int(current_index) + 1]
    except Exception:
        return None


@register.simple_tag
def new_width(iframe, width):
    res = re.sub(r'width="\d{1,3}"', 'width="'+str(width)+'%"', iframe)
    return res


@register.simple_tag
def get_starting_index(length):
    return length[len(length)-2:len(length)]


@register.simple_tag
def get_content_length(page):
    counter = 0
    for block in page.body:
        if block.block_type == 'content':
            counter += 1
    return counter

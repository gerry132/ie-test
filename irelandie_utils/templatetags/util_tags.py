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


@register.simple_tag
def new_width(iframe, width):
    print(1243)
    print(1243)
    print(1243)
    print(1243)
    print(1243)
    print(width)
    res = re.sub(r'width="\d{1,3}"', 'width="'+str(width)+'%"', iframe)
    print(res)
    return res
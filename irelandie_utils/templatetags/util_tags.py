# -*- coding: utf-8 -*-
from django import template
from django.utils.text import camel_case_to_spaces, slugify

from irelandie_home.models import HomePage
from irelandie_missions.models import MissionPage
from irelandie_pages.models import FreeFormPage
from irelandie_utils.models import SocialMediaSettings

import re

import uuid

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
def return_date_from_datetime(date_obj):
    return date_obj.strftime("%b. %d, %Y")


@register.simple_tag
def title_length(title):
    return len(str(title))


@register.simple_tag
def new_width(iframe, width):
    res = re.sub(r'width="\d{1,3}"', 'width="' + str(width) + '%"', iframe)
    return res


@register.simple_tag
def get_starting_index(length):
    return length[len(length) - 2:len(length)]


@register.simple_tag
def get_unique_ref():
    ref = uuid.uuid4().hex
    return ref


@register.simple_tag
def get_content_length(page):
    counter = 0
    for block in page.body:
        if block.block_type == 'content':
            counter += 1
    return counter


@register.simple_tag
def get_mega_menu_length(menus):
    counter = 0
    for block in menus:
        counter += 1
    return counter


@register.simple_tag
def format_date(date):
    return date.strftime('%d %B %Y')


@register.simple_tag
def get_admin_content_length(page):
    counter = 0
    for block in page.admin_body1:
        if block.block_type in ['admin_contents', 'contact_details']:
            counter += 1
    return counter


@register.simple_tag
def get_admin_contents_length(page):
    counter = 0
    for block in page.admin_body2:
        if block.block_type in ['admin_content', 'contact_details']:
            counter += 1
    return counter


@register.simple_tag
def count_toc(page):
    result = get_admin_content_length(page) + get_admin_contents_length(page) + get_content_length(page)
    return result


@register.simple_tag
def favicon_child(page):
    if isinstance(page, int) or isinstance(page, str):
        # accounts for search
        return False
    pages = page.get_ancestors()

    for p in pages:
        if p.content_type.name == 'mission page':
            m = MissionPage.objects.get(id=p.id)
            if m.favicon:
                return m.favicon

    for p in pages:
        if p.content_type.name == 'Free Form Page':
            f = FreeFormPage.objects.get(id=p.id)
            if f.favicon:
                return f.favicon

    for p in pages:
        if p.content_type.name == 'Free Form Page Base':
            h = HomePage.objects.get(id=p.id)
            if h.favicon:
                return h.favicon

    return False


@register.simple_tag(
    takes_context=True
)
def verify_path(context):
    request = context['request']

    if 'localhost' in request.get_host():
        return {'content': True, 'host': 'localhost'}
    content_url_map = {
        'content.ireland.ie': 'ireland.ie',
        'content.uat.ireland.ie': 'uat.ireland.ie',
        'content.preprod.ireland.ie': 'preprod.ireland.ie'
    }

    if request.get_host() in content_url_map.keys():
        return {'content': True,
                'host': content_url_map[request.get_host()]}

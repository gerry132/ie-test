# -*- coding: utf-8 -*-
from django import template
from django.utils.text import camel_case_to_spaces, slugify

from irelandie_home.models import HomePage
from irelandie_missions.models import MissionPage
from irelandie_pages.models import FreeFormPage
from irelandie_utils.models import SocialMediaSettings

from datetime import datetime

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
    return date_obj.strftime("%b %d %Y")


@register.simple_tag
def todays_date():
    return return_date_from_datetime(datetime.today())


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
def format_date(date):
    if isinstance(date, str):
        return datetime.strptime(date, '%d %B %Y')
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
def lists(stories, stats):
    list_stories = stories
    n = len(list_stories)
    list_stats = list(stats)
    return list_stories[0:2] + list_stats + list_stories[2:n]


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


@register.simple_tag
def get_category_tag(selected_tag, tags):
    counter = 0
    tagging = []
    for tag in tags:
        if tag == selected_tag:
            continue
        elif len(tags) == 2:
            return tag
        else:
            counter += 1
            tagging.append(tag)
            if counter == 2:
                return tagging


@register.simple_tag
def get_tag_links(tag, page):
    from irelandie_tags.models import TagLandingPage
    tagging_links = []
    tags_no_links = []
    tag_land = None
    for tags in tag:
        tag_landing = TagLandingPage.objects.live().filter(
            page_related_tags__page=tags, locale=page.locale).specific().distinct()
        for tag_land in tag_landing:
            tagging_links.append(list((tag_land.related_tags[0], tag_land.url)))
        if tag_land and tags == tag_land.related_tags[0]:
            continue
        else:
            tags_no_links.append(tags)
    return tagging_links, tags_no_links


@register.simple_tag
def get_category_tag_links(selected_tag, tag, page):
    from irelandie_tags.models import TagLandingPage
    tagging_links = []
    for tags in tag:
        if tags == selected_tag:
            continue
        else:
            tag_landing = TagLandingPage.objects.live().filter(
                page_related_tags__page=tags, locale=page.locale).specific().distinct()
            for tag_land in tag_landing:
                tagging_links.append(list((tag_land.related_tags[0], tag_land.url)))
    return tagging_links


@register.simple_tag
def get_category_tag_no_links(selected_tag, tag):
    tags_links = []
    tags_all = list(tag)
    for tag_links in selected_tag:
        tags_links.append(tag_links[0])
    new_list = list(set(tags_all).difference(tags_links))
    return new_list


@register.simple_tag
def get_destination_tag_links(tag):
    tagging_links = []
    for tags in tag:
        tagging_links.append(list((tags, tags.related_destinations[0])))
    return tagging_links


@register.simple_tag(
    takes_context=True
)
def verify_path(context):
    request = context['request']

    if 'localhost' in request.get_host():
        return {'content': False, 'host': 'localhost'}
    content_url_map = {
        'content.ireland.ie': 'ireland.ie',
        'content.uat.ireland.ie': 'uat.ireland.ie',
        'content.preprod.ireland.ie': 'preprod.ireland.ie'
    }

    if request.get_host() in content_url_map.keys():
        return {'content': True,
                'host': content_url_map[request.get_host()]}


@register.simple_tag
def get_travel_warning_by_locale(warning, locale):
    warning_map = {
        "normal precautions/gnáth-réamhchúraimí": {
            "English": "Normal Precautions",
            "Irish": "Gnáth-Réamhchúraimí"
        },
        "high degree of caution/bí an-chúramach": {
            "English": "High Degree of Caution",
            "Irish": "Bí an-chúramach",
        },
        "avoid non-essential travel/seachain taisteal neamhriachtanach": {
            "English": "Avoid Non-Essential Travel",
            "Irish": "Seachain Taisteal Neamhriachtanach",
        },
        "do not travel/ná taistil', 'do not travel/ná taistil": {
            "English": "Do Not Travel",
            "Irish": "Ná Taistil",
        }
    }

    reg = re.compile(r'<dd>.*<\/dd>')
    res = re.search(reg, str(warning))
    if res:
        res = res.group(0).strip(r'<d>|</d>')
        return warning_map[res][str(locale)]

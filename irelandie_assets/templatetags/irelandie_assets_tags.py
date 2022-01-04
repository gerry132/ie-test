# -*- coding: utf-8 -*-
from django import template


register = template.Library()


# -----------------------------------------------------------------------------
# SIMPLE TAGS
# -----------------------------------------------------------------------------

@register.simple_tag(takes_context=True)
def define(value):
    return value


@register.simple_tag(takes_context=True)
def project_title():
    return 'PROJECT TTITLE'


# -----------------------------------------------------------------------------
# INCLUSION TAGS
# -----------------------------------------------------------------------------

@register.inclusion_tag('irelandie_assets/components/navbars/footer.html', takes_context=True)
def footer(context):
    request = context.get('request', None)
    return {
        'request': request
    }


@register.inclusion_tag('irelandie_assets/components/navbars/main_menu.html', takes_context=True)
def main_menu(context):
    request = context.get('request', None)
    return {
        'request': request
    }


# -----------------------------------------------------------------------------
# FILTERS
# -----------------------------------------------------------------------------

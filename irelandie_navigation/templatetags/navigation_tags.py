# -*- coding: utf-8 -*-
from functools import lru_cache
from django import template
from wagtail.core.models import Locale

from irelandie_navigation.models import FooterNavigation, PrimaryNavigation, SecondaryNavigation

register = template.Library()


@lru_cache(maxsize=None)
def default_language():
    return Locale.objects.get(language_code="en")


def get_nav_for_locale(cls, locale):
    navigation = None

    try:
        navigation = cls.objects.get(locale=locale).navigation
    except cls.DoesNotExist:
        pass

    if not navigation:
        try:
            navigation = cls.objects.get(locale=default_language()).navigation
        except cls.DoesNotExist:
            pass

    return navigation


# PRIMARY NAVIGATION
# ----------------------------------------------------------------------
# The data for the primary navigation is managed in the PrimaryNavigation
# snippets model.
@register.inclusion_tag(
    "patterns/molecules/navigation/primarynav.html", takes_context=True
)
def primarynav(context):
    request = context["request"]
    locale = Locale.objects.get(language_code=request.LANGUAGE_CODE)

    navigation = get_nav_for_locale(PrimaryNavigation, locale)

    return {
        "primarynav": navigation,
        "request": request,
    }


# SECONDARY NAVIGATION
# ----------------------------------------------------------------------
# The data for the secondary navigation is managed in the SecondaryNavigation
# snippets model.
@register.inclusion_tag(
    "patterns/molecules/navigation/secondarynav.html", takes_context=True
)
def secondarynav(context):
    request = context["request"]
    locale = Locale.objects.get(language_code=request.LANGUAGE_CODE)

    navigation = get_nav_for_locale(SecondaryNavigation, locale)

    return {
        "secondarynav": navigation,
        "request": request,
    }


@register.simple_tag(
    takes_context=True
)
def has_secondary_nav(context):
    request = context["request"]
    locale = Locale.objects.get(language_code=request.LANGUAGE_CODE)
    return bool(get_nav_for_locale(SecondaryNavigation, locale))


# FOOTER NAVIGATION
# ----------------------------------------------------------------------
# The data for the footer navigation is managed in the FooterNavigation
# snippets model.
@register.inclusion_tag(
    "patterns/molecules/navigation/footernav.html", takes_context=True
)
def footernav(context):
    request = context["request"]
    locale = Locale.objects.get(language_code=request.LANGUAGE_CODE)

    navigation = get_nav_for_locale(FooterNavigation, locale)

    return {
        "footernav": navigation,
        "request": request,
    }


# FOOTER LINKS
# ----------------------------------------------------------------------
# The data for the footer links is managed in the FooterNavigation
# snippets model.
@register.inclusion_tag(
    "patterns/molecules/navigation/footerlinks.html", takes_context=True
)
def footerlinks(context):
    request = context["request"]
    locale = Locale.objects.get(language_code=request.LANGUAGE_CODE)

    navigation = None

    try:
        navigation = FooterNavigation.objects.get(locale=locale).links
    except FooterNavigation.DoesNotExist:
        pass

    if not navigation:
        try:
            navigation = FooterNavigation.objects.get(locale=default_language()).links
        except FooterNavigation.DoesNotExist:
            pass

    return {
        "footerlinks": navigation,
        "request": request,
    }


# items below may be removed once confirmed they are not needed


# Secondary nav snippets
# @register.inclusion_tag(
#     "patterns/molecules/navigation/secondarynav.html", takes_context=True
# )
# def secondarynav(context):
#     request = context["request"]
#     return {
#         "secondarynav": context["settings"]["irelandie_navigation"][
#             "NavigationSettings"
#         ].secondary_navigation,
#         "request": request,
#     }


# Footer nav snippets
@register.inclusion_tag(
    "patterns/molecules/navigation/sidebar.html", takes_context=True
)
def sidebar(context):
    return {
        "children": context["page"].get_children().live().public().in_menu(),
        "request": context["request"],
    }


# Custom primary navigation
@register.inclusion_tag(
    "patterns/molecules/navigation/custom_primary_navigation.html", takes_context=True
)
def custom_primary_navigation(context, current_page):
    return {
        "customnav": current_page.custom_primary_navigation,
        "request": context["request"],
    }

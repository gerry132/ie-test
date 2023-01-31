# -*- coding: utf-8 -*-

from functools import lru_cache
from django import template
from wagtail.models import Locale

from irelandie_navigation.models import (
    CustomFooter,
    FooterNavigation,
    PrimaryNavigation,
    SecondaryNavigation,
    SiteSettings,
    CustomHeader,
)

from irelandie_missions.models import MissionPage
from irelandie_pages.models import FreeFormPage
from irelandie_utils.models import SocialMediaSettings

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
def primarynav(context, page, override=None):
    request = context["request"]
    locale = Locale.objects.get(language_code=request.LANGUAGE_CODE)

    navigation = get_nav_for_locale(PrimaryNavigation, locale)

    try:
        custom_header = CustomHeader.objects.get(id=page.custom_header.id)
    except AttributeError:
        custom_header = None

    return {
        "primarynav": navigation,
        "customnav": custom_header,
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


@register.simple_tag(
    takes_context=True
)
def has_root_override(context, page, header=True):
    if isinstance(page, int) or isinstance(page, str):
        # accounts for search
        return False

    pages = page.get_ancestors()

    for p in pages:
        if p.content_type.name == 'mission page':
            m = MissionPage.objects.get(id=p.id)
            if m.root_page:
                if header:
                    return m.custom_header
                else:
                    return m.custom_footer

    for p in pages:
        if p.content_type.name == 'Free Form Page':
            f = FreeFormPage.objects.live().get(id=p.id)
            if f.root_page:
                if header:
                    return f.custom_header
                else:
                    return f.custom_footer

    return False


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


@register.inclusion_tag(
    "patterns/molecules/navigation/footernav.html", takes_context=True
)
def customfooternav(context, custom_footer):
    request = context["request"]

    return {
        "request": request,
        "footernav": custom_footer,
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


# CUSTOM FOOTER SETTINGS
# ----------------------------------------------------------------------
# The data for the custom footer navigation is managed in the CustomFooter
# snippets model. It's an optional field on pages via a snippet chooser in the
# promote tab.
# The purpose of this template tag is to reduce the amount of if: elif: else: conditionals
# needed in the footer.html template.

@register.simple_tag(takes_context=True)
def custom_footer_settings(context, page):
    request = context["request"]

    locale = Locale.objects.get(language_code=request.LANGUAGE_CODE)
    site_settings = SiteSettings.for_request(request)
    footer_social_media = SocialMediaSettings.for_request(request)
    footer_navigation = None

    try:
        footer_navigation = FooterNavigation.objects.get(locale=locale)
    except FooterNavigation.DoesNotExist:
        pass

    if not footer_navigation:
        try:
            footer_navigation = FooterNavigation.objects.get(locale=default_language())
        except FooterNavigation.DoesNotExist:
            pass

    try:
        custom_footer = CustomFooter.objects.get(id=page.custom_footer.id)
    except AttributeError:
        custom_footer = None

    if custom_footer:
        # if custom footer is set for the page, use the values from it if they are set
        # otherwise use the site settings values
        logo = custom_footer.logo or site_settings.site_logo
        mobile_logo = custom_footer.mobile_logo
        page = custom_footer.page
        url = custom_footer.url or None
        logo_alt = custom_footer.logo_alt or site_settings.site_logo_alt
        twitter_handle = custom_footer.twitter_handle or footer_social_media.twitter_handle
        facebook_app_id = custom_footer.facebook_app_id or footer_social_media.facebook_app_id
        youtube_user = custom_footer.youtube_user or footer_social_media.youtube_user
        linkedin_profile = custom_footer.linkedin_profile or footer_social_media.linkedin_profile
        instagram_user = custom_footer.instagram_user or footer_social_media.instagram_user
        show_social_media = any(
            [
                twitter_handle,
                facebook_app_id,
                youtube_user,
                linkedin_profile,
                instagram_user,
            ]
        )
        navigation = custom_footer.navigation
        links = custom_footer.links

    else:
        # no custom footer is set for the page, use the site settings
        # if thr site settings has values for the fields
        logo = site_settings.site_logo
        mobile_logo = site_settings.mobile_logo
        logo_alt = site_settings.site_logo_alt
        twitter_handle = footer_social_media.twitter_handle
        facebook_app_id = footer_social_media.facebook_app_id
        youtube_user = footer_social_media.youtube_user
        linkedin_profile = footer_social_media.linkedin_profile
        instagram_user = footer_social_media.instagram_user
        url = None
        show_social_media = any(
            [
                twitter_handle,
                facebook_app_id,
                youtube_user,
                linkedin_profile,
                instagram_user,
            ]
        )
        if footer_navigation:
            navigation = footer_navigation.navigation
            links = footer_navigation.links
        else:
            navigation = None
            links = None

    return {
        "logo": logo,
        "mobile_logo": mobile_logo,
        "logo_alt": logo_alt,
        "page": page,
        "url": url,
        "twitter_handle": twitter_handle,
        "facebook_app_id": facebook_app_id,
        "youtube_user": youtube_user,
        "linkedin_profile": linkedin_profile,
        "instagram_user": instagram_user,
        "show_social_media": show_social_media,
        "navigation": navigation,
        "links": links,
    }


# CUSTOM HEADER SETTINGS
# ----------------------------------------------------------------------
# The data for the custom header navigation is managed in the CustomHeader
# snippets model. It's an optional field on pages via a snippet chooser in the
# promote tab.
# The purpose of this template tag is to reduce the amount of if: elif: else: conditionals
# needed in the footer.html template.

@register.simple_tag(takes_context=True)
def custom_header_settings(context, page):
    request = context["request"]

    site_settings = SiteSettings.for_request(request)

    try:
        custom_header = CustomHeader.objects.get(id=page.custom_header.id)
    except AttributeError:
        custom_header = None

    if custom_header:
        # if custom header is set for the page, use the values from it if they are set
        # otherwise use the site settings values
        logo = custom_header.logo or site_settings.site_logo
        mobile_logo = custom_header.mobile_logo
        logo_alt = custom_header.logo_alt or site_settings.site_logo_alt
        links = custom_header.links
        url = custom_header.url
        link_page = custom_header.link_page
        is_present = True
    else:
        # no custom header is set for the page, use the site settings
        # if the site settings has values for the fields
        logo = site_settings.site_logo
        mobile_logo = site_settings.mobile_logo
        logo_alt = site_settings.site_logo_alt
        links = None
        url = None
        is_present = False
        link_page = None

    return {
        "url": url,
        "logo": logo,
        "mobile_logo": mobile_logo,
        "logo_alt": logo_alt,
        "links": links,
        "link_page": link_page,
        "site_settings": site_settings,
        "is_present": is_present
    }

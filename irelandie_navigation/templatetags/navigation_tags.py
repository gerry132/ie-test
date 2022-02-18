from django import template
from wagtail.core.models import Locale

from irelandie_navigation.models import FooterNavigation, PrimaryNavigation

register = template.Library()


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
    try:
        navigation = PrimaryNavigation.objects.get(locale=locale).navigation
    except PrimaryNavigation.DoesNotExist:
        navigation = None

    return {
        "primarynav": navigation,
        "request": request,
    }


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
    try:
        navigation = FooterNavigation.objects.get(locale=locale).navigation
    except FooterNavigation.DoesNotExist:
        navigation = None

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
    try:
        navigation = FooterNavigation.objects.get(locale=locale).links
    except FooterNavigation.DoesNotExist:
        navigation = None

    return {"footerlinks": navigation, "request": request}


"""items below may be removed once confirmed they are not needed"""


# Secondary nav snippets
@register.inclusion_tag(
    "patterns/molecules/navigation/secondarynav.html", takes_context=True
)
def secondarynav(context):
    request = context["request"]
    return {
        "secondarynav": context["settings"]["irelandie_navigation"][
            "NavigationSettings"
        ].secondary_navigation,
        "request": request,
    }


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
def custom_primary_navigtaion(context, current_page):
    return {
        "customnav": current_page.custom_primary_navigation,
        "request": context["request"],
    }

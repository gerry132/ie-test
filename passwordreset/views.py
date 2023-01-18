from collections import OrderedDict
from datetime import timedelta
from wagtail import hooks
from wagtail.users.models import UserProfile

from django.db import transaction
from django.utils.translation import gettext_lazy, override
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect

from django.utils.translation import gettext as _

from django.forms import Media

from django.template.response import TemplateResponse
from django.utils import timezone


from .panels import ChangePasswordPanel


def password_management_enabled():
    return True


class SettingsTab:
    def __init__(self, name, title, order=0):
        self.name = name
        self.title = title
        self.order = order


profile_tab = SettingsTab("profile", gettext_lazy("Profile"), order=100)


def force_password_reset(request):
    user = request.user
    profile = UserProfile.get_for_user(user)

    # Panels
    panels = [
        ChangePasswordPanel(request, user, profile),
    ]
    for fn in hooks.get_hooks("register_account_settings_panel"):
        panel = fn(request, user, profile)
        if panel and panel.is_active():
            panels.append(panel)

    panels = [panel for panel in panels if panel.is_active()]

    # Get tabs and order them
    tabs = list({panel.tab for panel in panels})
    tabs.sort(key=lambda tab: tab.order)

    # Get dict of tabs to ordered panels
    panels_by_tab = OrderedDict([(tab, []) for tab in tabs])
    for panel in panels:
        panels_by_tab[panel.tab].append(panel)
    for tab, tab_panels in panels_by_tab.items():
        tab_panels.sort(key=lambda panel: panel.order)

    panel_forms = [panel.get_form() for panel in panels]

    if request.method == "POST":
        if all(form.is_valid() or not form.is_bound for form in panel_forms):
            with transaction.atomic():
                for form in panel_forms:
                    if form.is_bound:
                        form.save()

            # Prevent a password change from logging this user out
            update_session_auth_hash(request, user)
            user.password_reset = timezone.now() + timedelta(minutes=87600)
            user.reset_lock = False
            user.save()

            # Override the language when creating the success message
            # If the user has changed their language in this request, the message should
            # be in the new language, not the existing one
            with override(profile.get_preferred_language()):
                messages.success(
                    request, _("Your password has been updated successfully!")
                )

            return redirect("wagtailadmin_account")

    media = Media()
    for form in panel_forms:
        media += form.media

    # Menu items
    menu_items = []
    for fn in hooks.get_hooks("register_account_menu_item"):
        item = fn(request)
        if item:
            menu_items.append(item)

    return TemplateResponse(
        request,
        "passwordreset/index.html",
        {
            "panels_by_tab": panels_by_tab,
            "menu_items": menu_items,
            "media": media,
        },
    )

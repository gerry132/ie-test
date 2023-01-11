from django.utils.translation import gettext_lazy
from django.template.loader import render_to_string
from wagtail.admin.forms.auth import PasswordChangeForm


def password_management_enabled():
    return True


class SettingsTab:
    def __init__(self, name, title, order=0):
        self.name = name
        self.title = title
        self.order = order


profile_tab = SettingsTab("profile", gettext_lazy("Profile"), order=100)


class BaseSettingsPanel:
    name = ""
    title = ""
    tab = profile_tab
    help_text = None
    template_name = "wagtailadmin/account/settings_panels/base.html"
    form_class = None
    form_object = "user"

    def __init__(self, request, user, profile):
        self.request = request
        self.user = user
        self.profile = profile

    def is_active(self):
        """
        Returns True to display the panel.
        """
        return True

    def get_form(self):
        """
        Returns an initialised form.
        """
        kwargs = {
            "instance": self.profile if self.form_object == "profile" else self.user,
            "prefix": self.name,
        }

        if self.request.method == "POST":
            return self.form_class(self.request.POST, self.request.FILES, **kwargs)
        else:
            return self.form_class(**kwargs)

    def get_context_data(self):
        """
        Returns the template context to use when rendering the template.
        """
        return {"form": self.get_form()}

    def render(self):
        """
        Renders the panel using the template specified in .template_name and context from .get_context_data()
        """
        return render_to_string(
            self.template_name, self.get_context_data(), request=self.request
        )


class ChangePasswordPanel(BaseSettingsPanel):
    name = "password"
    title = gettext_lazy("Password")
    order = 500
    form_class = PasswordChangeForm

    def is_active(self):
        return password_management_enabled() and self.user.has_usable_password()

    def get_form(self):
        # Note: don't bind the form unless a field is specified
        # This prevents the validation error from displaying if the user wishes to ignore this
        bind_form = False
        if self.request.method == "POST":
            bind_form = any(
                [
                    self.request.POST.get(self.name + "-old_password"),
                    self.request.POST.get(self.name + "-new_password1"),
                    self.request.POST.get(self.name + "-new_password2"),
                ]
            )

        if bind_form:
            return self.form_class(self.user, self.request.POST, prefix=self.name)
        else:
            return self.form_class(self.user, prefix=self.name)

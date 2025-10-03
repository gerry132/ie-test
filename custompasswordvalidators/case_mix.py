import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CaseMixValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password) or not re.findall('[a-z]', password):
            raise ValidationError(
                _("The password must a mixture of uppercase and lowercase letters."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _(
            "The password must a mixture of uppercase and lowercase letters."
        )

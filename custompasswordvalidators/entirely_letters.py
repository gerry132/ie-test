import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class EntirelyLettersValidator(object):
    def validate(self, password, user=None):
        if len(re.findall(r'\d', password)) == 0:
            raise ValidationError(
                _("The password must contain numbers as well as letters."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain numbers as well as letters."
        )

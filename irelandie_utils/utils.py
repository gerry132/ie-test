from wagtail.models import Locale


def get_locale_from_language_code_or_default(language_code):
    try:
        locale = Locale.objects.get(language_code=language_code)
    except Locale.DoesNotExist:
        locale = Locale.get_default()

    return locale

import unicodedata

from django.utils.translation import get_language_info
from wagtail.models import Locale as Locale
import locale


def local_languages(request):
    locales = Locale.objects.all()
    languages = []
    for wagtail_locale in locales:

        lang_code = wagtail_locale.language_code
        if lang_code == 'ch':
            lang_code = 'zh-hans'
        languages.append([lang_code, get_language_info(lang_code)["name_local"]])

    return {
        "local_languages": sorted(
            languages, key=lambda x: locale.strxfrm(unicodedata.normalize('NFD', x[1])).casefold())
    }

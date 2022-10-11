from wagtail.models import Locale


def get_locale_from_language_code_or_default(language_code):
    try:
        locale = Locale.objects.get(language_code=language_code)
    except Locale.DoesNotExist:
        locale = Locale.get_default()

    return locale

def get_model_info(Model, pk):
    from irelandie_missions.models import MissionPage
    from irelandie_pages.models import FreeFormPage
    model_map = {
        'Free Form Page': FreeFormPage,
        'mission page': MissionPage
    }

    return model_map[Model].objects.live().get(id=pk)

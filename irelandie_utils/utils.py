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

    return model_map[Model].objects.get(id=pk)


def get_root_info(context, pages):
    from irelandie_missions.models import MissionPage
    from irelandie_pages.models import FreeFormPage

    page_map = {
        'mission page': MissionPage,
        'Free Form Page': FreeFormPage
    }
    root_found = False
    for p in pages:
        if p.content_type.name in page_map.keys():
            missions = page_map[p.content_type.name].objects.live().get(id=p.id)
            if missions.root_page:
                context['default_image'] = missions.default_image
                context['mission_web_bot'] = missions.web_bot_script
                root_found = True
    return context, root_found

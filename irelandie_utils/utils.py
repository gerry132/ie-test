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
    from irelandie_missions.models import DestinationPage

    model_map = {
        'Free Form Page': FreeFormPage,
        'mission page': MissionPage,
        'destination page': DestinationPage
    }

    return model_map[Model].objects.get(id=pk)


def get_root_info(context, pages, current_page=None):
    from irelandie_missions.models import MissionPage, DestinationPage
    from irelandie_pages.models import FreeFormPage

    page_map = {
        'mission page': MissionPage,
        'Free Form Page': FreeFormPage,
        'destination page': DestinationPage,
    }

    root_found = False

    if current_page and isinstance(current_page, MissionPage) and getattr(current_page, "root_page", None):
        if hasattr(current_page, "default_image"):
            context["default_image"] = current_page.default_image
        context["mission_web_bot"] = getattr(current_page, "web_bot_script", None)
        context["root_page"] = current_page
        return context, True

    for p in pages:
        if p.content_type.name in page_map:
            page_cls = page_map[p.content_type.name]
            page_obj = page_cls.objects.get(id=p.id)

            if getattr(page_obj, "root_page", None):
                if hasattr(page_obj, "default_image"):
                    context["default_image"] = page_obj.default_image
                context["mission_web_bot"] = getattr(page_obj, "web_bot_script", None)
                context["root_page"] = page_obj
                root_found = True
                break

    return context, root_found

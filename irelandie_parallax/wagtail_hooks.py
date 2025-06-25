from wagtail import hooks
from django.templatetags.static import static
from django.utils.html import format_html


@hooks.register('insert_editor_js')
def editor_js():
    return format_html('<script src="{}"></script>', static('js/main.js'))

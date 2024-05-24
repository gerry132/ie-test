from wagtail import hooks

from .views import tag_chooser_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return tag_chooser_viewset

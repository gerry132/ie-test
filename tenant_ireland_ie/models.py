from django.db import models

from type_homepage.models import AbstractHomepagePage

from .conf import settings


class HomepagePage(AbstractHomepagePage):

    class Meta:
        default_related_name = f'{settings.RELATED_NAME_PREFIX}_homepage_page'
        verbose_name = _(f'{settings.SITE_DOMAIN} home page')
        verbose_name_plural = _(f'{settings.SITE_DOMAIN} home pages')

    max_count = 1
    subpage_types = []
    template = ''

    content_panels = AbstractHomepagePage.content_panels + []

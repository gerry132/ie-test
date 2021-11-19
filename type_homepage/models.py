# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _

from wagtail.core.models import Page, TranslatableMixin


class AbstractHomepagePage(Page, TranslatableMixin):

    class Meta:
        abstract = True
        verbose_name = _('Home page')
        verbose_name_plural = _('Home pages')

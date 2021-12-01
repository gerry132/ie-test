# -*- coding: utf-8 -*-
from django.conf import settings as dj_settings
from django.utils.text import slugify


class Settings:

    VAR_NAME_IRELAND_IE_SITE_DOMAIN = 'IRELAND_IE_SITE_DOMAIN'
    VAR_NAME_IRELAND_IE_ERROR_TEMPLATE = 'IRELAND_IE_ERROR_TEMPLATE'
    VAR_NAME_IRELAND_IE_HOMEPAGE_TEMPLATE = 'IRELAND_IE_HOMEPAGE_TEMPLATE'

    @property
    def RELATED_NAME_PREFIX(self):
        return slugify(self.SITE_DOMAIN)

    @property
    def SITE_DOMAIN(self):
        return getattr(
            dj_settings,
            self.VAR_NAME_IRELAND_IE_SITE_DOMAIN,
            'localhost:8000'
        )

    @property
    def ERROR_TEMPLATE(self):
        return getattr(
            dj_settings,
            self.VAR_NAME_IRELAND_IE_ERROR_TEMPLATE,
            'tenant_ireland_ie/pages/error_page.html'
        )

    @property
    def HOMEPAGE_TEMPLATE(self):
        return getattr(
            dj_settings,
            self.VAR_NAME_IRELAND_IE_HOMEPAGE_TEMPLATE,
            'tenant_ireland_ie/pages/homepage.html'
        )


settings = Settings()

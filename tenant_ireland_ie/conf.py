from django.conf import settings as dj_settings
from django.utils.text import slugify


class Settings:

    VAR_NAME_IRELAND_IE_SITE_DOMAIN = 'IRELAND_IE_SITE_DOMAIN'

    @property
    def SITE_DOMAIN(self):
        return getattr(
            dj_settings,
            self.VAR_NAME_IRELAND_IE_SITE_DOMAIN,
            'localhost:8000'
        )

    @property
    def RELATED_NAME_PREFIX(self):
        return slugify(self.SITE_DOMAIN)


settings = Settings()

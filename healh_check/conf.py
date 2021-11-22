# -*- coding: utf-8 -*-
import re

from django.conf import settings as dj_settings


class Settings:

    VAR_NAME_HEALTH_CHECK_PATH = 'HEALTH_CHECK_PATH'

    def HEALTH_CHECK_PATTERN(self):

        path = getattr(
            dj_settings,
            self.VAR_NAME_HEALTH_CHECK_PATH,
            '/health-check/'
        )

        return re.sub(r'(^\/)', '', path)


settings = Settings()

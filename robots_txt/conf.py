# -*- coding: utf-8 -*-
import re

from django.conf import settings as dj_settings


class Settings:

    @property
    def ROBOTS_PATTERN(self):

        path = '/robots.txt'

        return re.sub(r'(^\/)', '', path)


settings = Settings()

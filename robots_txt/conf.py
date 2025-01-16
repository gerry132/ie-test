# -*- coding: utf-8 -*-
import re


class Settings:

    @property
    def ROBOTS_PATTERN(self):

        path = '/robots.txt'

        return re.sub(r'(^\/)', '', path)


settings = Settings()

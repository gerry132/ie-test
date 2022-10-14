# -*- coding: utf-8 -*-
from django.apps import AppConfig
import sys


class UtilsConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "irelandie_utils"
    label = "utils"

    def ready(self):
        if 'runserver' not in sys.argv:
            return True
        from .agent.pub_unpub_agent import Agent
        agent = Agent()
        print(agent)

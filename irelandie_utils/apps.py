# -*- coding: utf-8 -*-
from django.apps import AppConfig


class UtilsConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "irelandie_utils"
    label = "utils"

    def ready(self):
        from .agent.pub_unpub_agent import Agent
        agent = Agent()
        print(agent)

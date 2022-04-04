# -*- coding: utf-8 -*-
from django.db import models


class SocialMediaFieldsMixin(models.Model):
    twitter_handle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Your Twitter username without the @, e.g. katyperry",
    )
    facebook_app_id = models.CharField(
        max_length=255, blank=True, help_text="Your Facebook app ID."
    )
    youtube_user = models.CharField(
        max_length=255, blank=True, help_text="Your YouTube username."
    )
    linkedin_profile = models.CharField(
        max_length=255, blank=True, help_text="Your LinkedIn profile URL."
    )

    class Meta:
        abstract = True

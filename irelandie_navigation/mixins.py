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
    linkedin_profile = models.URLField(blank=True, help_text="Your LinkedIn profile URL."
                                       )
    instagram_user = models.CharField(
        max_length=255, blank=True, help_text="Your Instagram username."
    )
    weibo_user = models.CharField(
        max_length=255, blank=True, help_text="Your Weibo username."
    )

    class Meta:
        abstract = True

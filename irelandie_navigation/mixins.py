# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

HOST_NAMES = ['twitter.com', 'www.facebook.com', 'youtube.com', 'instagram.com', 'www.weibo.com']


def validate_hostname(value):
    if not value:
        return  # Required error is done the field
    obj = urlparse(value)
    if obj.hostname in HOST_NAMES:
        raise ValidationError(f'Only add the social media handle here, e.g. if the full link is '
                              f'https://{obj.hostname}/myprofile, type myprofile into this box.')


class SocialMediaFieldsMixin(models.Model):
    twitter_handle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Your Twitter username without the @, e.g. katyperry",
        validators=[validate_hostname]
    )
    facebook_app_id = models.CharField(
        max_length=255, blank=True, help_text="Your Facebook app ID.",
        validators=[validate_hostname]
    )
    youtube_user = models.CharField(
        max_length=255, blank=True, help_text="Your YouTube username.",
        validators=[validate_hostname]
    )
    linkedin_profile = models.URLField(blank=True, help_text="Your LinkedIn profile URL.",
                                       )
    instagram_user = models.CharField(
        max_length=255, blank=True, help_text="Your Instagram username.",
        validators=[validate_hostname]
    )
    weibo_user = models.CharField(
        max_length=255, blank=True, help_text="Your Weibo username.",
        validators=[validate_hostname]
    )

    class Meta:
        abstract = True

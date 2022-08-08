from django.db import models


class StoryAlignment(models.TextChoices):
    LEFT = 'left', 'Left'
    RIGHT = 'right', 'Right'


class StoryBackground(models.TextChoices):
    LIGHT = 'light', 'Light'
    DARK = 'dark', 'Dark'

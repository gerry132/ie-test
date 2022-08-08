from django.db import models


class StoryAlignment(models.TextChoices):
    LEFT = 'left', 'Left'
    RIGHT = 'right', 'Right'


class StoryBackground(models.TextChoices):
    LIGHT = 'light', 'Light'
    DARK = 'dark', 'Dark'


class ParagraphAlignment(models.TextChoices):
    WIDE = 'wide', 'Wide'
    NARROW = 'narrow', 'Narrow'

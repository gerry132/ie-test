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


class TravelRegions(models.TextChoices):
    ASIA_AND_OCEANIA = 'asia and oceania', 'Asia and Oceania'
    MIDDLE_EAST_AND_NORTH_AFRICA = 'middle east and north africa', 'Middle East and North Africa'
    NORTH_AND_CENTRAL_AMERICA = 'north and central america', 'North and Central America'
    SOUTH_AMERICA = 'south america', 'South America'
    SUB_SAHARAN_AFRICA = 'sub-suharan africa', 'Sub-Saharan Africa'
    CARIBBEAN = 'caribbean', 'Caribbean'


class TravelCautionLevel(models.TextChoices):
    NORMAL_PRECAUTIONS = 'normal precations/' \
        'gnáth-réamhchúraimí', 'normal precations/Gnáth-réamhchúraimí'
    HIGH_DEGREE_OF_CAUTION = 'high degree of caution/' \
        'bí an-chúramach', 'High Degree of Caution/Bí an-chúramach'
    AVOID_NON_ESSENTIAL_TRAVEL = 'avoid non-essential travel/seachain ' \
        'taisteal neamhriachtanach', 'Avoid Non-Essential Travel/Seachain Taisteal Neamhriachtanach'
    DO_NOT_TRAVEL = 'do not travel/ná taistil', 'do not travel/Ná Taistil'

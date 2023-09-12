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
    SUB_SAHARAN_AFRICA = 'sub-saharan africa', 'Sub-Saharan Africa'
    CARIBBEAN = 'caribbean', 'Caribbean'
    EUROPE = 'europe', 'Europe'


class TravelCautionLevel(models.TextChoices):
    NORMAL_PRECAUTIONS = 'normal precautions/' \
                         'gnáth-réamhchúraimí', 'Normal Precautions/Gnáth-Réamhchúraimí'
    HIGH_DEGREE_OF_CAUTION = 'high degree of caution/' \
                             'bí an-chúramach', 'High Degree of Caution/Bí An-Chúramach'
    AVOID_NON_ESSENTIAL_TRAVEL = 'avoid non-essential travel/' \
                                 'seachain taisteal neamhriachtanach', 'Avoid Non-Essential Travel/Seachain Taisteal ' \
                                                                       'Neamhriachtanach'
    DO_NOT_TRAVEL = 'do not travel/' \
                    'ná taistil', 'Do Not Travel/Ná Taistil'


class NoticeIcon(models.TextChoices):
    CHOOSE_AN_ICON = '', 'Choose an icon'
    EMERGENCY = 'emergency', 'Emergency'
    INFORMATION = 'information', 'Information'


class YoutubeSize(models.TextChoices):
    SMALL = 'small', 'Small'
    MEDIUM = 'medium', 'Medium'
    LARGE = 'large', 'Large'


class USAStates(models.TextChoices):
    CHOOSE_A_STATE = '', 'State'
    Alabama = 'al', 'AL'
    Alaska = 'ak', 'AK'
    Arizona = 'az', 'AZ'
    Arkansas = 'ar', 'AR'
    California = 'ca', 'CA',
    Colorado = 'co', 'CO'
    Connecticut = 'ct', 'CT'
    Delaware = 'de', 'DE'
    District_of_Columbia = 'dc', 'DC'
    Florida = 'fl', 'FL',
    Georgia = 'ga', 'GA',
    Hawaii = 'hi', 'HI'
    Idaho = 'id', 'ID'
    Illinois = 'il', 'IL'
    Indiana = 'in', 'IN'
    Iowa = 'ia', 'IA'
    Kansas = 'ks', 'KS'
    Kentucky = 'ky', 'KY'
    Louisiana = 'la', 'LA'
    Maine = 'me', 'ME'
    Maryland = 'md', 'MD'
    Massachusetts = 'ma', 'MA'
    Michigan = 'mi', 'MI'
    Minnesota = 'mn', 'MN'
    Mississippi = 'ms', 'MS'
    Missouri = 'mo', 'MO'
    Montana = 'mt', 'MT'
    Nebraska = 'ne', 'NE'
    Nevada = 'nv', 'NV'
    New_Hampshire = 'nh', 'NH'
    New_Jersey = 'nj', 'NJ'
    New_Mexico = 'nm', 'NM'
    New_York = 'ny', 'NY'
    North_Carolina = 'nc', 'NC'
    North_Dakota = 'nd', 'ND'
    Ohio = 'oh', 'OH'
    Oklahoma = 'ok', 'OK'
    Oregon = 'or', 'OR'
    Pennsylvania = 'pa', 'PA'
    Rhode_Island = 'ri', 'RI'
    South_Carolina = 'sc', 'SC'
    South_Dakota = 'sd', 'SD'
    Tennessee = 'tn', 'TN'
    Texas = 'tx', 'TX'
    Utah = 'ut', 'UT'
    Vermont = 'vt', 'VT'
    Virginia = 'va', 'VA'
    Washington = 'wa', 'WA'
    West_Virginia = 'wv', 'WV'
    Wisconsin = 'wi', 'WI'
    Wyoming = 'wy', 'WY'

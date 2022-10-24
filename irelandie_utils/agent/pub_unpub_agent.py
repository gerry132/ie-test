from datetime import datetime
import pytz
from irelandie_utils.agent.time_thread import RepeatedTimer
from irelandie_corporate_information.models import CorportateInformationPageIndex
from irelandie_missions.models import (
    CountryGroupPageIndex,
    JobContentPage,
    JobIndexPage,
    ServiceContent,
    ServicesLandingPage,
    MissionSearchPage
)

from irelandie_news.models import (
    NewsLandingPage,
    NewsPageIndex,
    NewsPage
)

from irelandie_press_releases.models import PressReleasePage
from irelandie_speeches.models import SpeechPage
from django.db.models import Q
from django.core import management

class Agent(RepeatedTimer):
    def __init__(self):
        super().__init__(120, self.unpub_pub_pages)
    
    def unpub_pub_pages(self, **kwargs):
        print(12345)
        management.call_command('publish_scheduled_pages')
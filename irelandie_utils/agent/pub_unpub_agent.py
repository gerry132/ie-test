from datetime import datetime
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


class Agent(RepeatedTimer):
    def __init__(self):
        super().__init__(900, self.get_obj)
        self.models = [
            CountryGroupPageIndex,
            JobContentPage,
            JobIndexPage,
            ServiceContent,
            ServicesLandingPage,
            MissionSearchPage,
            NewsLandingPage,
            NewsPageIndex,
            NewsPage,
            PressReleasePage,
            SpeechPage,
            CorportateInformationPageIndex
        ]

    def get_obj(self):
        for model in self.models:
            print("STARTING POLL")
            try:
                go_live = model.objects.filter(
                                go_live_at__lte=datetime.now()).filter(live=False)
                expired = model.objects.filter(
                    expire_at__lte=datetime.now()).filter(live=True)
                self.update_obj(go_live, True)
                self.update_obj(expired, False)
                print(model)
            except Exception as e:
                print(e)

    def update_obj(self, obj_l, pub):
        for page in obj_l:
            page.live = pub
            if pub:
                page.first_published_at = datetime.now()
            page.save()

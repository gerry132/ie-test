from irelandie_utils.agent.time_thread import RepeatedTimer
from django.core import management

class Agent(RepeatedTimer):
    def __init__(self):
        super().__init__(120, self.unpub_pub_pages)

    def unpub_pub_pages(self, **kwargs):
        print(12345)
        management.call_command('publish_scheduled_pages')

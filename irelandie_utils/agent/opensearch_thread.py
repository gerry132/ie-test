from irelandie_utils.agent.time_thread import RepeatedTimer
from django.core import management


class OpensearchAgent(RepeatedTimer):
    def __init__(self):
        super().__init__(1200, self.rebuild_indices)

    def rebuild_indices(self, **kwargs):
        management.call_command('wagtail_update_index')

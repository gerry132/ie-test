from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page

class EventListPageRoutabilityTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        Page.objects.create(title='test', path='/', depth=1)

    def test_default_route(self):
        self.page = Page.objects.get(id=1)
        self.assertPageIsRenderable(self.page, route_path="/", accept_404=True)

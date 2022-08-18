import unittest
from irelandie_utils.blocks import BaseBlockLinkContext


# Need to improve these tests with DjangoModelFactory
class TestPage:
    def __init__(self):
        self.owner = "John Doe"
        self.url = "http://dummy-page.com"
        self.title = "This is the page title"


class TestBaseBlockLinkContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = TestPage()

    def test_internal_link_with_title(self):
        value = {
            "url": None,
            "page": self.page,
            "title": "internal-dummy-title"
        }

        context = BaseBlockLinkContext().get_context(value)
        self.assertEqual(context["link_title"],
                         "internal-dummy-title")

    def test_internal_link_without_title(self):
        value = {
            "url": None,
            "page": self.page,
            "title": None
        }
        context = BaseBlockLinkContext().get_context(value)
        self.assertEqual(context["link_title"],
                         "This is the page title")

    def test_external_link_with_title(self):
        value = {
            "url": "http://dummy-url.com",
            "page": None,
            "title": "external-dummy-title"
        }

        context = BaseBlockLinkContext().get_context(value)
        self.assertEqual(context["link_title"],
                         "external-dummy-title")

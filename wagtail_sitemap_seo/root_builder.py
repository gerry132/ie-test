import xml.etree.cElementTree as ET
import pandas as pd

from wagtail.models import Page
from wagtail.core.models import Locale

from django.conf import settings


from .base import BaseBuilder


def email_management_enabled():
    return getattr(settings, "WAGTAIL_EMAIL_MANAGEMENT_ENABLED", True)


class RootBuilder(BaseBuilder):

    def __init__(self, root_file):
        self.root_file = root_file
        self.root_pages = []
        self.page_url_map = {}
        self.site = None

    def site_map_init(self, root=False):
        xml_root = ET.Element('urlset')
        xml_root.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        xml_root.attrib['xsi:schemaLocation'] = "http://www.sitemaps.org/schemas/sitemap/0.9" \
            + " http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
        xml_root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
        print(settings.SEO_MAP_URL)
        return xml_root

    def add_xml_root(self, xml_root):
        for url in self.root_pages:
            elem = self.build_root_elem(url)
            xml_root.append(elem)

        tree = ET.ElementTree(xml_root)
        tree.write('sitemap.xml', encoding='utf-8', xml_declaration=True)

    def get_site(self):
        return self.site

    def _load_urls_from_root(self):
        if settings.SEO_MAP_URL:
            urls = pd.read_csv(settings.SEO_MAP_URL)
        else:
            urls = pd.read_csv('wagtail_sitemap_seo/test.csv')
        header = urls.columns[0]

        # TODO: perhaps add multisite support
        self.site = header
        for series in urls[header]:
            locale = Locale.objects.get(language_code='en')
            p = Page.objects.live().filter(slug=series.strip("/"), locale=locale)

            for res in p:
                self.page_url_map[series] = res
                self.root_pages.append(res)

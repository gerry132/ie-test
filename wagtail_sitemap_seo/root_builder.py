import xml.etree.cElementTree as ET
import csv
import urllib.request

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
        xml_root.attrib['xmlns:xsi'] = "https://www.w3.org/2001/XMLSchema-instance"
        xml_root.attrib['xmlns:xhtml'] = "https://www.w3.org/1999/xhtml"
        xml_root.attrib['xsi:schemaLocation'] = "https://www.sitemaps.org/schemas/sitemap/0.9" \
            + " https://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
        xml_root.attrib['xmlns'] = "https://www.sitemaps.org/schemas/sitemap/0.9"
        print(settings.SEO_MAP_URL)
        return xml_root

    def add_xml_root(self, xml_root):
        for url in self.root_pages:
            elem = self.build_root_elem(url)
            xml_root.append(elem)

        tree = ET.ElementTree(xml_root)
        tree.write('root_map.xml', encoding='utf-8', xml_declaration=True)

    def get_site(self):
        return self.site

    def _load_urls_from_root(self):
        urls = []
        if settings.SEO_MAP_URL:
            response = urllib.request.urlopen(settings.SEO_MAP_URL)
            lines = [l.decode('utf-8') for l in response.readlines()]
            cr = csv.reader(lines)

            for row in cr:
                urls.append(row[0])
            self.site = urls[0]
            urls.remove(self.site)

        # TODO: perhaps add multisite support

            for series in urls:
                locale = Locale.objects.get(language_code='en')
                p = Page.objects.live().filter(slug=series.strip("/"), locale=locale)

                for res in p:
                    self.page_url_map[series] = res
                    self.root_pages.append(res)

from irelandie_utils.agent.time_thread import RepeatedTimer
from wagtail_sitemap_seo.sub_map_builder import MapBuilder


class Agent(RepeatedTimer):
    def __init__(self):
        super().__init__(10, self.builder_run)

    def builder_run(self, **kwargs):
        root = MapBuilder('test.csv')
        root._load_urls_from_root()
        root_map = root.site_map_init()
        root.add_xml_root(root_map)

        for page in root.root_pages:
            root.build_map(page)

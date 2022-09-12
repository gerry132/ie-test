from wagtail import blocks


class NewsPageBlock(blocks.PageChooserBlock):

    def __init__(self):
        super().__init__("irelandie_news.NewsPage")

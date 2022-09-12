from wagtail import blocks


class PublicationPageBlock(blocks.PageChooserBlock):

    def __init__(self):
        super().__init__("irelandie_publications.PublicationPage")

from wagtail import blocks


class SiteInformationPageBlock(blocks.PageChooserBlock):

    def __init__(self):
        super().__init__("irelandie_site_information.SiteInformationPage")

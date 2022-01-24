from wagtail.core import blocks


class CorportateInformationPageBlock(blocks.PageChooserBlock):

    def __init__(self):
        super().__init__("irelandie_corporate_information.CorportateInformationPage")

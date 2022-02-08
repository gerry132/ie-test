from wagtail.core import blocks


class PressReleasePageBlock(blocks.PageChooserBlock):

    def __init__(self):
        super().__init__("irelandie_press_releases.PressReleasePage")

from wagtail import blocks


class SpeechPageBlock(blocks.PageChooserBlock):

    def __init__(self):
        super().__init__("irelandie_speeches.SpeechPage")

from wagtail import blocks
from wagtail.core.blocks import StreamBlock, ChoiceBlock
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from wagtail.images.blocks import ImageChooserBlock
from irelandie_utils.constants import ParagraphAlignment, TextAlignment
from irelandie_utils.blocks import (
    StoryVideoBlock, TimelinePhotoGalleriesBlock, ImageButtonBlock,
    CustomVideoChooserBlock, StoryPhotoGalleriesBlock, LogoCardsBlock,
    AdvancedRichTextBlock, LinkCardsBlock, ALT_HELP_TEXT_IMG_VIDEO)
from wagtail.blocks.struct_block import StructBlockValidationError
from irelandie_home.blocks import SecondaryCallToAction


class ParallaxAdvancedRichTextBlock(blocks.StructBlock):
    is_speakable = blocks.BooleanBlock(required=False, default=False, help_text="Mark if this block is speakable")
    section_id = blocks.CharBlock(required=False)
    background_color = blocks.CharBlock(max_length=7, default='#ffffff', required=False)
    audio = blocks.RawHTMLBlock(
        group="HTML",
        help_text="Add title attribute value to iframe for accessibility.",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
        required=False,
    )
    paragraph_alignment = blocks.ChoiceBlock(
        required=False,
        choices=ParagraphAlignment.choices,
        default=ParagraphAlignment.NARROW,
    )
    text_alignment = blocks.ChoiceBlock(
        required=False,
        choices=TextAlignment.choices,
        default=TextAlignment.CENTER,
    )
    text_color = blocks.CharBlock(max_length=7, default='#020202', required=False)
    link_color = blocks.CharBlock(
        max_length=7, required=False, default="#004d46",
        help_text="Hex color for hyperlinks in this block"
    )
    heading = blocks.CharBlock(required=False)
    rich_text = blocks.RichTextBlock(
        features=["h2", "h3", "h4", "blockquote", "bold", "link", "document-link", "ul", "ol"], required=False,
    )
    button_link = blocks.StreamBlock(
        [
            ("color", blocks.StructBlock([
                ("button_color", blocks.CharBlock(max_length=7, required=False)),
                ("button_text_color", blocks.CharBlock(max_length=7, required=False)),
            ]
            )),
            ("button", SecondaryCallToAction())
        ],
        blank=True,
        block_counts={
            "button": {"max_num": 1},
            "color": {"max_num": 1},
        },
        required=False,
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        button_color = None
        button_text_color = None
        buttons = []
        for item in value.get('button_link', []):
            if item.block_type == "color":
                button_color = item.value.get('button_color')
                button_text_color = item.value.get('button_text_color')
            elif item.block_type == "button":
                buttons.append(item.value)

        context['button_color'] = button_color
        context['button_text_color'] = button_text_color
        context['buttons'] = buttons

        return context

    class Meta:
        label = "Parallax Advanced RichTextBlock"
        template = "patterns/molecules/streamfield/blocks/parallax_advanced_richtext_block.html"


class ParallaxImageVideoBlock(blocks.StructBlock):
    is_speakable = blocks.BooleanBlock(required=False, default=False, help_text="Mark if this block is speakable")
    section_id = blocks.CharBlock(required=False)
    gradient_image_video = blocks.CharBlock(max_length=7, default='#000', required=False)
    image = ImageChooserBlock(required=False, label="Desktop Image")
    mobile_image = ImageChooserBlock(required=False)
    video = CustomVideoChooserBlock(required=False, label="Desktop Video")
    mobile_video = CustomVideoChooserBlock(required=False, label="Mobile Video")
    alt_text = blocks.CharBlock(
        required=True,
        help_text=_(ALT_HELP_TEXT_IMG_VIDEO),
    )
    image_video_credits = blocks.CharBlock(required=False)
    text_alignment = blocks.ChoiceBlock(
        required=False,
        choices=TextAlignment.choices,
        default=TextAlignment.CENTER,
    )
    text_color = blocks.CharBlock(max_length=7, default='#020202', required=False)
    link_color = blocks.CharBlock(
        max_length=7, required=False, default="#004d46",
        help_text="Hex color for hyperlinks in this block"
    )
    heading = blocks.CharBlock(blank=True, required=False)
    subtitle = blocks.RichTextBlock(blank=True, required=False)

    def clean(self, value):
        errors = {}

        image = value.get('image')
        video = value.get('video')
        mobile_image = value.get('mobile_image')
        mobile_video = value.get('mobile_video')

        if not (bool(image) ^ bool(video)):
            msg = "You can't choose both an image and a video. Choose an image or a video"
            errors['image'] = ErrorList([msg])
            errors['video'] = ErrorList([msg])

        if not (bool(image) | bool(video)):
            msg = "You have to choose either an image or a video."
            errors['image'] = ErrorList([msg])
            errors['video'] = ErrorList([msg])

        if image and mobile_video:
            msg = "You selected an image for desktop and a video for mobile. Please use an image or a video."
            errors['mobile_video'] = ErrorList([msg])
            errors['image'] = ErrorList([msg])

        if video and mobile_image:
            msg = "You selected a video for desktop and an image for mobile. Please use a video or an image."
            errors['mobile_image'] = ErrorList([msg])
            errors['video'] = ErrorList([msg])

        if mobile_image and mobile_video:
            msg = "You added both a mobile image and a mobile video. Please choose only one for mobile."
            errors['mobile_image'] = ErrorList([msg])
            errors['mobile_video'] = ErrorList([msg])

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)

    class Meta:
        label = "parallax Image/Video Block"
        template = "patterns/molecules/streamfield/blocks/parallax_imagevideo_block.html"


class ParallaxLogoCardsBlock(blocks.StructBlock):
    is_speakable = blocks.BooleanBlock(required=False, default=False, help_text="Mark if this block is speakable")
    background_color = blocks.CharBlock(max_length=7, default='#ffffff', required=False)
    text_color = blocks.CharBlock(max_length=7, default='#020202', required=False)
    link_color = blocks.CharBlock(
        max_length=7, required=False, default="#004d46",
        help_text="Hex color for hyperlinks in this block"
    )
    text_alignment = blocks.ChoiceBlock(
        required=False,
        choices=TextAlignment.choices,
        default=TextAlignment.CENTER,
    )
    button_color = blocks.CharBlock(
        max_length=7, required=False,
        help_text="Background color for buttons"
    )
    button_text_color = blocks.CharBlock(
        max_length=7, required=False,
        help_text="Text color for buttons"
    )
    logo_cards = LogoCardsBlock()

    class Meta:
        label = 'Parallax Logocards'
        template = "patterns/molecules/streamfield/blocks/parallax_blocks.html"


class ParallaxStoryPhotoGalleryBlock(blocks.StructBlock):
    is_speakable = blocks.BooleanBlock(required=False, default=False, help_text="Mark if this block is speakable")
    background_color = blocks.CharBlock(max_length=7, default='#ffffff', required=False)
    text_color = blocks.CharBlock(max_length=7, default='#020202', required=False)
    link_color = blocks.CharBlock(
        max_length=7, required=False, default="#004d46",
        help_text="Hex color for hyperlinks in this block"
    )
    text_alignment = blocks.ChoiceBlock(
        required=False,
        choices=TextAlignment.choices,
        default=TextAlignment.CENTER,
    )
    button_color = blocks.CharBlock(
        max_length=7, required=False,
        help_text="Background color for buttons"
    )
    button_text_color = blocks.CharBlock(
        max_length=7, required=False,
        help_text="Text color for buttons"
    )
    story_photo_gallery = StoryPhotoGalleriesBlock()

    class Meta:
        label = 'Parallax Story Photo Gallery'
        template = "patterns/molecules/streamfield/blocks/parallax_blocks.html"


class ParallaxTimelinePhotoGalleryBlock(blocks.StructBlock):
    is_speakable = blocks.BooleanBlock(required=False, default=False, help_text="Mark if this block is speakable")
    background_color = blocks.CharBlock(max_length=7, default='#ffffff', required=False)
    text_color = blocks.CharBlock(max_length=7, default='#020202', required=False)
    link_color = blocks.CharBlock(
        max_length=7, required=False, default="#004d46",
        help_text="Hex color for hyperlinks in this block"
    )
    text_alignment = blocks.ChoiceBlock(
        required=False,
        choices=TextAlignment.choices,
        default=TextAlignment.CENTER,
    )
    button_color = blocks.CharBlock(
        max_length=7, required=False,
        help_text="Background color for buttons"
    )
    button_text_color = blocks.CharBlock(
        max_length=7, required=False,
        help_text="Text color for buttons"
    )
    timeline_photo_gallery = TimelinePhotoGalleriesBlock()

    class Meta:
        label = 'Parallax Timeline Photo Gallery'
        template = "patterns/molecules/streamfield/blocks/parallax_blocks.html"


class ParallaxLinkCardsBlock(blocks.StructBlock):
    is_speakable = blocks.BooleanBlock(required=False, default=False, help_text="Mark if this block is speakable")
    background_color = blocks.CharBlock(max_length=7, default='#ffffff', required=False)
    text_color = blocks.CharBlock(max_length=7, default='#020202', required=False)
    link_color = blocks.CharBlock(
        max_length=7, required=False, default="#004d46",
        help_text="Hex color for hyperlinks in this block"
    )
    text_alignment = blocks.ChoiceBlock(
        required=False,
        choices=TextAlignment.choices,
        default=TextAlignment.CENTER,
    )
    button_color = blocks.CharBlock(
        max_length=7, required=False,
        help_text="Background color for buttons"
    )
    button_text_color = blocks.CharBlock(
        max_length=7, required=False,
        help_text="Text color for buttons"
    )
    richtext = AdvancedRichTextBlock(required=False)
    link_cards = LinkCardsBlock()

    class Meta:
        label = 'Parallax Link cards'
        template = "patterns/molecules/streamfield/blocks/parallax_blocks.html"


class ParallaxYoutubeVimeoBlock(blocks.StructBlock):
    is_speakable = blocks.BooleanBlock(required=False, default=False, help_text="Mark if this block is speakable")
    section_id = blocks.CharBlock(required=False)
    background_color = blocks.CharBlock(max_length=7, default='#ffffff', required=False)
    text_color = blocks.CharBlock(max_length=7, default='#020202', required=False)
    text_alignment = blocks.ChoiceBlock(
        required=False,
        choices=TextAlignment.choices,
        default=TextAlignment.CENTER,
    )
    youtube_or_vimeo_video = StoryVideoBlock()

    class Meta:
        label = 'Parallax Youtube/Vimeo Embed'
        template = "patterns/molecules/streamfield/blocks/parallax_blocks.html"


class DoubleFeature(StreamBlock):
    rich_text = ParallaxAdvancedRichTextBlock()
    image_video = ParallaxImageVideoBlock()
    gradient_colour = blocks.CharBlock(required=False)
    gradient_alignment = ChoiceBlock(
        choices=[
            ("none", "None"),
            ("left", "Left"),
            ("right", "Right"),
        ],
        default="none",
        label="Choose Layout"
    )

    def clean(self, value):
        value = super().clean(value)
        core_blocks = []

        for block in value:
            if block.block_type not in ["gradient_alignment", "gradient_colour"]:
                core_blocks.append(block)

        if len(core_blocks) > 2:
            raise ValidationError("You can only add a maximum of 2 blocks in total.")
        return value

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        gradient_alignment = "none"
        gradient_colour = "none"
        core_blocks = []
        button_color = None
        button_text_color = None
        buttons = []

        for block in value:
            if block.block_type == "gradient_alignment":
                gradient_alignment = block.value  # Store the selected choice
            elif block.block_type == "gradient_colour":
                gradient_colour = block.value
            else:
                core_blocks.append(block)

                # If this is your rich_text block, get its context to retrieve buttons
                if block.block_type == "rich_text":
                    rich_text_context = block.block.get_context(block.value, parent_context)
                    button_color = rich_text_context.get("button_color")
                    button_text_color = rich_text_context.get("button_text_color")
                    buttons = rich_text_context.get("buttons")

        context["core_blocks"] = core_blocks  # Store the non-gradient blocks
        context["gradient_alignment"] = gradient_alignment  # Store the alignment
        context["gradient_colour"] = gradient_colour
        context["button_color"] = button_color
        context["button_text_color"] = button_text_color
        context["buttons"] = buttons

        return context

    class Meta:
        label = 'Double Feature'
        template = "patterns/molecules/streamfield/blocks/parallax_double_feature.html"

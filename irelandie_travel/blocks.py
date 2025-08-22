from django.core.exceptions import ValidationError

from irelandie_home.blocks import SecondaryCallToAction
from irelandie_utils.blocks import AdvancedRichTextBlock, LinkButtonBlock, ImageChooserBlock
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock

from irelandie_utils.constants import TravelCautionLevel, TravelRegions


class AlteredAvancedRichTextBlock(AdvancedRichTextBlock):
    button_links = blocks.StreamBlock(
        [
            ("button", SecondaryCallToAction())
        ],
        blank=True,
        min_num=0,
        required=False,
    )


class InformationBlock(blocks.StreamBlock):
    richtext = AdvancedRichTextBlock()


class ButtonBlock(blocks.StreamBlock):
    button = LinkButtonBlock()
    image = ImageChooserBlock()


class TravelCautionBlock(blocks.StructBlock):
    travel_caution_level = blocks.ChoiceBlock(
        required=True,
        choices=TravelCautionLevel.choices,
        default=TravelCautionLevel.NORMAL_PRECAUTIONS
    )


class TravelRegionBlock(blocks.StructBlock):
    region = blocks.ChoiceBlock(
        required=True,
        choices=TravelRegions.choices,
        default=TravelRegions.ASIA_AND_OCEANIA,
    )


class TravelIndexOuterBlock(blocks.StreamBlock):
    rich_text = AdvancedRichTextBlock()
    travel_snippet = SnippetChooserBlock(target_model="utils.TravelSnippet")


class TravelIndexOuterBlockBool(blocks.StructBlock):
    travel = TravelIndexOuterBlock()
    apply_color = blocks.BooleanBlock(required=False)


class UniqueChoiceBlock(blocks.ChoiceBlock):
    class Meta:
        form_classname = "unique-choice-block"


class RegionalAdvisoriesChoiceBlock(blocks.StructBlock):
    travel_caution_level = UniqueChoiceBlock(
        required=True,
        choices=TravelCautionLevel.choices,
    )


class RegionalAdvisoriesBlock(blocks.ListBlock):

    def __init__(self, **kwargs):
        super().__init__(RegionalAdvisoriesChoiceBlock(), min_num=0, max_num=4, **kwargs)

    def clean(self, value):
        cleaned_data = super().clean(value)

        levels = [item.get('travel_caution_level') for item in cleaned_data]

        # Find duplicates
        duplicates = set([lvl for lvl in levels if levels.count(lvl) > 1])

        if duplicates:
            # Raise field-specific errors
            errors = []
            for i, item in enumerate(cleaned_data):
                if item.get("travel_caution_level") in duplicates:
                    errors.append(ValidationError({
                        'travel_caution_level': ValidationError(
                            "This advisory level is duplicated.",
                            code="duplicate"
                        )
                    }))
                else:
                    errors.append(None)

            raise ValidationError(errors)

        return cleaned_data

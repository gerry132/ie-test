import os
import re
from django.core.exceptions import ValidationError
from django.db import models
from wagtail.images import get_image_model_string
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from django.utils.translation import gettext as _


class CustomImage(AbstractImage):
    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        help_text=_(
            "Please use a unique, meaningful filename. Avoid generic names like "
            "'image.jpg' and use descriptive titles that match the content of the image."
        ),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Alt text"),
        help_text=_(
            "Say what the image means (who/what/action or essential text). "
            "Be neutral and brief (50–120 characters). Don't write 'image of...', "
            "filenames, or keywords."
        ),
    )

    admin_form_fields = Image.admin_form_fields

    def clean(self):
        super().clean()

        if self.file:
            filename = os.path.basename(self.file.name).lower()
            existing = CustomImage.objects.filter(file__iexact=filename)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({
                    "file": _(
                        "An image with this filename already exists in the media library. Please rename it before "
                        "uploading, using a specific and descriptive filename to help identify the image."
                    )
                })

        if not self.description or not self.description.strip():
            raise ValidationError({
                "description": _("Alt text is required. Please describe the image briefly.")
            })

        if re.search(r"\.(jpg|jpeg|png|gif|webp)$", self.description, re.IGNORECASE):
            raise ValidationError({
                "description": _("Do not use filenames as alt text.")
            })

        if not re.search(r"[A-Za-z]", self.description):
            raise ValidationError({
                "description": _("Alt text must contain letters.")
            })


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.CASCADE,
        related_name="renditions",
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)

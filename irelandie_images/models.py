import os

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.images import get_image_model_string
from wagtail.images.models import AbstractImage, AbstractRendition, Image


class CustomImage(AbstractImage):
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
                    "file": "An image with this filename already exists in the media library. Please rename it before "
                            "uploading, using a specific and descriptive filename to help identify the image."
                })


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(get_image_model_string(), on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)

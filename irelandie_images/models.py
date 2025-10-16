import os

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.images import get_image_model_string
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from django.utils.translation import gettext as _


class CustomImage(AbstractImage):
    title = models.CharField(max_length=255, verbose_name=_("title"), help_text="Please use a unique, meaningful "
                                                                                "filename. Avoid generic names like "
                                                                                "'image.jpg' and use descriptive "
                                                                                "titles that match the content of the "
                                                                                "image.")
    admin_form_fields = Image.admin_form_fields
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("Used as the default alt text when inserting images.")
    )

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

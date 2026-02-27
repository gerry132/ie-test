from import_export import resources
from django.core.exceptions import ValidationError

from .models import DiasporaDirectory, REGION_CHOICES


class DiasporaDirectoryResource(resources.ModelResource):
    class Meta:
        model = DiasporaDirectory
        fields = (
            "main_regions",
            "organisation_name",
            "contact_details",
            "city",
            "region",
            "website",
            "activity",
        )
        import_id_fields = ("organisation_name", "main_regions", "region")
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """
        Expect CSV to provide main_regions as the DB value (e.g. USA, IRL, ...).
        """
        allowed = {value for value, _label in REGION_CHOICES}
        val = (row.get("main_regions") or "").strip()
        if val and val not in allowed:
            raise ValidationError(
                f"Invalid main_regions '{val}'. Allowed values: {', '.join(sorted(allowed))}"
            )

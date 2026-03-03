from import_export import resources
from .models import DiasporaDirectory


class DiasporaDirectoryResource(resources.ModelResource):
    class Meta:
        model = DiasporaDirectory
        fields = (
            "organisation_name",
            "contact_details",
            "city",
            "region",
            "website",
            "activity",
            "country",
            "phone_number",
            "email",
            "seeking_volunteers",
        )
        import_id_fields = ("organisation_name", "country", "region")
        skip_unchanged = True
        report_skipped = True

import json
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps
from wagtail.models import Page
from wagtail.images import get_image_model

Image = get_image_model()


class Command(BaseCommand):
    help = "Restore alt text from backup"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Preview only")
        parser.add_argument("--path", type=str, default=None, help="Backup JSON path")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        backup_path = options["path"] or (
                Path(settings.BASE_DIR) / "backups" / "image_alt_backup.json")

        if not backup_path.exists():
            return

        with backup_path.open("r", encoding="utf-8") as f:
            backup = json.load(f)

        restored = 0

        for image_id_str, data in backup.items():
            for usage in data.get("found_alts", []):
                restored += self.restore_single_field(usage, dry_run)

    def restore_single_field(self, usage, dry_run):
        obj_type = usage["obj_type"]
        obj_id = usage["obj_id"]
        alt_field = usage["alt_field"]
        alt_text = usage["alt"]

        try:
            if obj_type == "Page":
                obj = Page.objects.get(id=obj_id)
            else:
                try:
                    model = apps.get_model(obj_type)
                    obj = model.objects.get(id=obj_id)
                except (LookupError, model.DoesNotExist):
                    return 0

            current_val = getattr(obj, alt_field, None)
            if str(current_val or "").strip() == alt_text:
                return 0

            if not dry_run:
                setattr(obj, alt_field, alt_text)
                obj.save(update_fields=[alt_field])
                return 1

        except Exception as e:
            self.stdout.write(f"Error {obj_type}.{obj_id}.{alt_field}: {e}")

        return 0

import json
from collections import defaultdict
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import ForeignKey
from wagtail.models import Page
from wagtail.blocks import StructValue, StreamValue
from wagtail.images import get_image_model
from wagtail.snippets.models import get_snippet_models
from wagtail.contrib.settings.models import BaseSiteSetting
from pathlib import Path
from django.conf import settings

Image = get_image_model()


class Command(BaseCommand):
    help = "Migrate ALL alt text (pages + snippets + StreamFields) → Image.description w/ field tracking"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Preview changes")

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.alt_usage = defaultdict(lambda: defaultdict(int))
        self.backup = {}

        # Scan everything
        for page in Page.objects.live().specific():
            self.scan_object(page)
        self.scan_snippets()
        self.scan_site_settings()

        self.apply_migration()
        self.write_backup()

    def scan_object(self, obj):
        self.scan_model_fields(obj)
        self.scan_streamfields(obj)

    def scan_model_fields(self, obj):
        image_alt_pairs = []

        image_fields = {}
        for field in obj._meta.fields:
            name = field.name

            if isinstance(field, ForeignKey) and field.related_model == Image:
                image = getattr(obj, name, None)
                if image:
                    image_fields[name] = image

            if "alt" in name.lower():
                alt_val = getattr(obj, name, None)
                if alt_val:
                    alt_text = str(alt_val).strip()
                    if alt_text:
                        for img_field, image in image_fields.items():
                            image_alt_pairs.append((image, img_field, name, alt_text))

        for image, img_field, alt_field, alt_text in image_alt_pairs:
            self.record(image, img_field, alt_field, alt_text, obj, "model_fields")

    def scan_streamfields(self, obj):
        for field in obj._meta.fields:
            value = getattr(obj, field.name, None)
            if isinstance(value, StreamValue):
                self.scan_streamvalue(value, obj, field.name)

    def scan_streamvalue(self, stream_value, obj, source):
        if not isinstance(stream_value, StreamValue):
            return
        for child in stream_value:
            self.scan_structvalue(child.value, obj, f"{source}.{child.block.name}")

    def scan_structvalue(self, struct_value, obj, source):
        if not isinstance(struct_value, StructValue):
            return

        image_alt_pairs = []
        images = {}
        alts = {}

        for key, val in struct_value.items():
            if hasattr(val, "id") and isinstance(val, Image):
                images[key] = val
            if "alt" in key.lower() and val:
                text = str(val).strip()
                if text:
                    alts[key] = text

        for img_key, image in images.items():
            alt_key = f"{img_key}_alt" if img_key != "image" else "image_alt"
            if alt_key in alts:
                image_alt_pairs.append((image, img_key, alt_key, alts[alt_key]))
            elif alts:
                alt_key = next(iter(alts))
                image_alt_pairs.append((image, img_key, alt_key, alts[alt_key]))

        for image, img_field, alt_field, alt_text in image_alt_pairs:
            self.record(image, img_field, alt_field, alt_text, obj, source)

        for key, val in struct_value.items():
            if isinstance(val, (StructValue, StreamValue)):
                self.scan_structvalue(val, obj, f"{source}.{key}")

    def scan_snippets(self):
        for model in get_snippet_models():
            for instance in model.objects.all():
                self.scan_object(instance)

    def scan_site_settings(self):
        for model in apps.get_models():
            if issubclass(model, BaseSiteSetting):
                for instance in model.objects.all():
                    self.scan_object(instance)

    def record(self, image, img_field, alt_field, alt_text, obj, source):
        self.alt_usage[image.id][alt_text] += 1
        self.backup.setdefault(str(image.id), {
            "library_alt_before": image.description,
            "found_alts": []
        })["found_alts"].append({
            "obj_type": obj.__class__.__name__,
            "obj_id": getattr(obj, 'id', 'N/A'),
            "source": source,
            "image_field": img_field,
            "alt_field": alt_field,
            "alt": alt_text
        })

    def apply_migration(self):
        updated = 0
        for image_id, alt_counts in self.alt_usage.items():
            image = Image.objects.filter(id=image_id).first()
            if image and not image.description:
                chosen_alt = self.choose_alt(alt_counts)
                if self.dry_run:
                    self.stdout.write(f"DRY-RUN: Image {image_id} → '{chosen_alt}'")
                else:
                    image.description = chosen_alt
                    image.save(update_fields=["description"])
                updated += 1
        return updated

    def choose_alt(self, alt_counts):
        max_count = max(alt_counts.values())
        candidates = [alt for alt, count in alt_counts.items() if count == max_count]
        return sorted(candidates)[0]

    def write_backup(self):
        backup_path = Path(settings.BASE_DIR) / "backups" / "image_alt_backup.json"
        backup_path.parent.mkdir(exist_ok=True)
        with backup_path.open("w", encoding="utf-8") as f:
            json.dump(self.backup, f, indent=2)

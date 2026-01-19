import json
from collections import defaultdict
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import ForeignKey
from wagtail.models import Page
from wagtail.blocks import StructValue, StreamValue
from wagtail.images import get_image_model
from django.db import models

Image = get_image_model()


class Command(BaseCommand):
    help = "Migrate ALL alt text (pages + ALL snippets + ALL models + StreamFields) into Image.description"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving",
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.alt_usage = defaultdict(lambda: defaultdict(int))
        self.backup = {}

        pages = Page.objects.live().specific()
        for page in pages:
            self.scan_object(page)

        self.scan_all_snippets()

        self.apply_migration()
        self.write_backup()

    def scan_object(self, obj):
        self.scan_model_fields(obj)
        self.scan_streamfields(obj)

    def scan_model_fields(self, obj):
        images = []
        alts = []

        for field in obj._meta.fields:
            name = field.name

            if isinstance(field, ForeignKey) and field.related_model == Image:
                image = getattr(obj, name, None)
                if image:
                    images.append(image)

            if "alt" in name.lower():
                val = getattr(obj, name, None)
                if val:
                    text = str(val).strip()
                    if text:
                        alts.append(text)

        if images and alts:
            model_name = obj.__class__.__name__
            self.record(images, alts, obj, f"{model_name}.fields")

    def scan_all_snippets(self):
        snippet_count = 0

        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                if not hasattr(model, '_meta') or not issubclass(model, models.Model):
                    continue

                try:
                    has_image_field = any(
                        isinstance(f, ForeignKey) and f.related_model == Image
                        for f in model._meta.fields
                    )

                    if has_image_field:
                        instances = model.objects.all()

                        for instance in instances:
                            self.scan_object(instance)
                            snippet_count += 1

                except Exception:
                    continue

    def scan_streamfields(self, obj):
        for field in obj._meta.fields:
            value = getattr(obj, field.name, None)
            if isinstance(value, StreamValue):
                self.scan_streamvalue(value, obj, field.name)

    def scan_streamvalue(self, stream_value, obj, source):
        if not isinstance(stream_value, StreamValue):
            return
        for child in stream_value:
            value = child.value
            if isinstance(value, StructValue):
                self.scan_structvalue(value, obj, source)
            elif isinstance(value, StreamValue):
                self.scan_streamvalue(value, obj, source)
            elif isinstance(value, list):
                self.scan_list(value, obj, source)

    def scan_list(self, items, obj, source):
        for item in items:
            if isinstance(item, StructValue):
                self.scan_structvalue(item, obj, source)
            elif isinstance(item, StreamValue):
                self.scan_streamvalue(item, obj, source)
            elif isinstance(item, list):
                self.scan_list(item, obj, source)

    def scan_structvalue(self, struct_value, obj, source):
        images_here = []
        alts_here = []

        for key, val in struct_value.items():
            if hasattr(val, "id") and isinstance(val, Image):
                images_here.append(val)
            if "alt" in key.lower() and val:
                text = str(val).strip()
                if text:
                    alts_here.append(text)

        if images_here and alts_here:
            self.record(images_here, alts_here, obj, source)

        # Recurse into nested blocks
        for key, val in struct_value.items():
            if isinstance(val, StructValue):
                self.scan_structvalue(val, obj, f"{source}.{key}")
            elif isinstance(val, StreamValue):
                self.scan_streamvalue(val, obj, f"{source}.{key}")
            elif isinstance(val, list):
                self.scan_list(val, obj, f"{source}.{key}")

    def record(self, images, alts, obj, source):
        if not images or not alts:
            return
        for image in images:
            for alt in alts:
                self.alt_usage[image.id][alt] += 1
                self.backup.setdefault(
                    str(image.id),
                    {"library_alt_before": image.description, "found_alts": []},
                )["found_alts"].append(
                    {
                        "obj_type": obj.__class__.__name__,
                        "obj_id": getattr(obj, 'id', 'N/A'),
                        "source": source,
                        "alt": alt,
                    }
                )

    def apply_migration(self):
        updated = 0
        for image_id, alt_counts in self.alt_usage.items():
            image = Image.objects.filter(id=image_id).first()
            if not image or image.description:
                continue
            chosen_alt = self.choose_alt(alt_counts)
            if not self.dry_run:
                image.description = chosen_alt
                image.save(update_fields=["description"])
            updated += 1
        return updated

    def choose_alt(self, alt_counts):
        max_count = max(alt_counts.values())
        candidates = [alt for alt, c in alt_counts.items() if c == max_count]
        return sorted(candidates)[0]

    def write_backup(self):
        with open("image_alt_backup.json", "w", encoding="utf-8") as f:
            json.dump(self.backup, f, indent=2)

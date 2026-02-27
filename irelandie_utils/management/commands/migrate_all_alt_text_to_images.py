from collections import defaultdict
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import ForeignKey
from wagtail.models import Page
from wagtail.blocks import StructValue, StreamValue
from wagtail.images import get_image_model
from wagtail.snippets.models import get_snippet_models
from wagtail.contrib.settings.models import BaseSiteSetting
from wagtail.fields import StreamField

Image = get_image_model()


class Command(BaseCommand):
    help = "Migrate ALL alt text (pages + snippets + StreamFields) → Image.description w/ field tracking"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Preview changes")

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.alt_usage = defaultdict(lambda: defaultdict(int))
        self.backup = {}

        self.stdout.write("[START] Alt migration started")

        # ---- Scan Pages ----
        self.stdout.write("[INFO] Scanning pages...")
        for page in Page.objects.live().specific().iterator(chunk_size=500):
            self.scan_object(page)
        self.stdout.write("[INFO] Page scan complete")

        # ---- Scan Snippets ----
        self.stdout.write("[INFO] Scanning snippets...")
        self.scan_snippets()
        self.stdout.write("[INFO] Snippet scan complete")

        # ---- Scan Site Settings ----
        self.stdout.write("[INFO] Scanning site settings...")
        self.scan_site_settings()
        self.stdout.write("[INFO] Site settings scan complete")

        # ---- Apply Migration ----
        self.stdout.write("[INFO] Applying migration...")
        updated_count = self.apply_migration()

        self.stdout.write(
            self.style.SUCCESS(f"[DONE] Migration complete. Images updated: {updated_count}")
        )

    def scan_object(self, obj):
        self.scan_model_fields(obj)
        self.scan_streamfields(obj)

    def scan_model_fields(self, obj):
        image_fields = {}
        for field in obj._meta.get_fields():
            if isinstance(field, ForeignKey) and field.related_model == Image:
                image = getattr(obj, field.name, None)
                if image:
                    image_fields[field.name] = image

        for field in obj._meta.get_fields():
            name = field.name
            if "alt" in name.lower():
                alt_val = getattr(obj, name, None)
                if alt_val:
                    alt_text = str(alt_val).strip()
                    if alt_text:
                        for img_field, image in image_fields.items():
                            self.record(image, img_field, name, alt_text, obj, "model_fields")

    def scan_streamfields(self, obj):
        for field in obj._meta.get_fields():
            if isinstance(field, StreamField):
                value = getattr(obj, field.name, None)
                if value:
                    self.scan_any(value, obj, field.name)

    def scan_any(self, value, obj, source):
        if isinstance(value, StreamValue):
            for child in value:
                self.scan_any(child.value, obj, f"{source}.{child.block.name}")

        elif isinstance(value, StructValue):
            images = {}
            alts = {}

            for key, val in value.items():
                if hasattr(val, "id") and isinstance(val, Image):
                    images[key] = val

                elif isinstance(val, str) and "alt" in key.lower():
                    text = val.strip()
                    if text:
                        alts[key] = text

            for img_key, image in images.items():
                for alt_key, alt_text in alts.items():
                    self.record(image, img_key, alt_key, alt_text, obj, source)

            for key, val in value.items():
                self.scan_any(val, obj, f"{source}.{key}")

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

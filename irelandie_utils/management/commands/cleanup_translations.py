from django.core.management.base import BaseCommand
from wagtail_localize.models import (
    StringSegment,
    TemplateSegment,
    Translation,
    TranslationSource,
    TranslationContext,
)


class Command(BaseCommand):
    help = "Clean up orphaned or invalid wagtail-localize translation segments, contexts, and sources."

    def handle(self, *args, **options):
        total_deleted = 0

        def clean(model, **filter_kwargs):
            nonlocal total_deleted
            qs = model.objects.filter(**filter_kwargs)
            count = qs.count()
        
            if count:
                self.stdout.write(f"Deleting {count} orphaned {model.__name__} records…")
                qs.delete()
                total_deleted += count

        # Remove segments missing context
        clean(StringSegment, context_id__isnull=True)
        clean(TemplateSegment, context_id__isnull=True)

        # Remove contexts missing object
        clean(TranslationContext, object_id__isnull=True)

        # Remove sources missing object
        clean(TranslationSource, object_id__isnull=True)

        # Remove translations missing source
        clean(Translation, source_id__isnull=True)

        if total_deleted:
            self.stdout.write(self.style.SUCCESS(f"✅ Cleanup complete. {total_deleted} records removed."))
        else:
            self.stdout.write(self.style.SUCCESS("✅ Nothing to clean — all translation data is consistent."))

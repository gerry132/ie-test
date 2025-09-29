from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = "Audits wagtailcore model schema fields against actual database columns"

    def get_existing_columns(self, table_name):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s
            """, [table_name])
            return {row[0] for row in cursor.fetchall()}

    def handle(self, *args, **options):
        self.stdout.write("🔍 Auditing Wagtail core schema...\n")
        core_models = [m for m in apps.get_app_config('wagtailcore').get_models()]
        missing_fields = {}

        for model in core_models:
            table_name = model._meta.db_table
            try:
                expected_fields = {
                    f.column for f in model._meta.fields
                    if not f.auto_created or f.concrete
                }
                actual_fields = self.get_existing_columns(table_name)
                missing = expected_fields - actual_fields
                if missing:
                    missing_fields[table_name] = sorted(missing)
            except Exception as e:
                missing_fields[table_name] = [f"(error checking model: {e})"]

        if not missing_fields:
            self.stdout.write(self.style.SUCCESS("✅ All Wagtail core schema fields are present and correct."))
        else:
            self.stdout.write(self.style.ERROR("❌ Missing fields detected:\n"))
            for table, fields in missing_fields.items():
                self.stdout.write(f"• {table}:\n    - " + "\n    - ".join(fields))
            self.stdout.write("\n🔧 Please manually restore these fields or check your migration history.")

from django.core.management.base import BaseCommand
from django.db import connection


EXPECTEDS = {
    "wagtailcore_revision": {
        "indexes": set(),
        "constraints": {"wagtailcore_revision_pkey"},
    },
    "wagtailcore_workflowstate": {
        "indexes": {"wagtailcore_workflowstate_page_id_idx"},
        "constraints": {"wagtailcore_workflowstate_page_id_fk"},
    },
    "wagtailcore_taskstate": {
        "indexes": {"wagtailcore_taskstate_page_revision_id_idx"},
        "constraints": {"wagtailcore_taskstate_page_revision_id_fk"},
    },
    "wagtailcore_groupapprovaltask": {
        "indexes": {"wagtailcore_groupapprovaltask_content_type_id_idx"},
        "constraints": {"wagtailcore_groupapprovaltask_content_type_id_fkey"},
    },
    "wagtailcore_grouppagepermission": {
        "indexes": set(),
        "constraints": {"wagtailcore_grouppagepermission_pkey"},
    },
}

class Command(BaseCommand):
    help = "Audit indexes and constraints on critical wagtailcore tables."

    def get_table_indexes_and_constraints(self, table):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = %s
            """, [table])
            indexes = {row[0] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_name = %s
            """, [table])
            constraints = {row[0] for row in cursor.fetchall()}

        return indexes, constraints

    def handle(self, *args, **options):
        self.stdout.write("🔍 Auditing critical indexes and constraints...\n")
        total_missing = 0

        for table, expected in EXPECTEDS.items():
            try:
                indexes, constraints = self.get_table_indexes_and_constraints(table)
                missing_indexes = expected["indexes"] - indexes
                missing_constraints = expected["constraints"] - constraints

                if missing_indexes or missing_constraints:
                    self.stdout.write(self.style.ERROR(f"❌ {table}:"))
                    for idx in missing_indexes:
                        self.stdout.write(f"    Missing index: {idx}")
                        total_missing += 1
                    for cst in missing_constraints:
                        self.stdout.write(f"    Missing constraint: {cst}")
                        total_missing += 1
                else:
                    self.stdout.write(self.style.SUCCESS(f"✅ {table} — OK"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Could not check {table}: {e}"))

        if total_missing == 0:
            self.stdout.write(self.style.SUCCESS("\n✅ All indexes and constraints are in place."))
        else:
            self.stdout.write(self.style.NOTICE(f"\n⚠️  Total missing: {total_missing} — consider restoring them manually."))


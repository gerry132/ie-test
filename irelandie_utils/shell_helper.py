from wagtail.blocks.stream_block import StreamValue
from wagtail.models import Page
from irelandie_home.models import HomePage

def func():
    from wagtail_localize.models import TemplateSegment

    import re

    deleted_count = 0

    for ts in TemplateSegment.objects.select_related("template").all():
        html = ts.template.template

        # Extract all numeric positions in <text position="..."> tags
        positions = [int(pos) for pos in re.findall(r'position="(\d+)"', html)]
        max_position = max(positions, default=-1)

        # ts has no .string_set or .string_count, so we estimate string count
        # by counting how many <text position="..."> there are — assume one per string
        approx_string_total = len(positions)

        # If there's a gap, it will break restore_strings() — e.g., if position="5" exists, but only 5 strings
        if max_position >= approx_string_total:
            print(f"🧹 Deleting TemplateSegment ID={ts.id} – max position={max_position}, but found only {approx_string_total} markers")
            ts.delete()
            deleted_count += 1

    print(f"✅ Deleted {deleted_count} broken TemplateSegment(s)")


from wagtail_localize.models import StringSegment

bad_paths = [
    "body.12c2b0b0-206e-4b72-895f-bb969d070341",
    "body.69fa2f0d-0b62-4a64-abeb-a90b0afb18f1.summary",
    "body.28ca35d8-bea6-4695-94b9-26c2ec1f302f.summary"
]

for path in bad_paths:
    deleted, _ = StringSegment.objects.filter(context__path=path).delete()
    print(f"🗑️ Deleted {deleted} StringSegment(s) for: {path}")



from wagtail_localize.models import StringSegment

bad_ids = ["12c2b0b0", "69fa2f0d"]
deleted_count = 0

for ss in StringSegment.objects.select_related("context"):
    context_path = getattr(ss.context, "path", "")
    if any(bad_id in context_path for bad_id in bad_ids):
        print(f"🧹 Deleting StringSegment ID={ss.id} with bad path: {context_path}")
        ss.delete()
        deleted_count += 1

print(f"✅ Deleted {deleted_count} corrupted StringSegment(s)")

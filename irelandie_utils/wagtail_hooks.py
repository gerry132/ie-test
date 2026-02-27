# irelandie_utils/wagtail_hooks.py

import csv
import io
from typing import Callable, Iterable, List, Optional, Tuple

from django import forms
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from wagtail import hooks
from wagtail.admin.auth import permission_required
from wagtail.admin.widgets.button import Button, ButtonWithDropdown
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import IndexView, SnippetViewSet

from .models import DiasporaDirectory, REGION_CHOICES


# ============================================================
# Shared helpers (reusable for any snippet import)
# ============================================================

class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label=_("CSV file"))


def clean(val) -> str:
    return str(val).replace("\xa0", " ").strip()


def read_csv_as_dicts(
    uploaded_file,
    *,
    required_columns: Optional[Iterable[str]] = None,
    delimiters: str = ";,",
) -> Tuple[csv.DictReader, List[str]]:
    """
    Robust CSV reader:
    - decodes using common encodings
    - sniffs delimiter (; or ,)
    - normalises headers (strip whitespace, drop blanks)
    Returns (DictReader, fieldnames)
    """
    raw = uploaded_file.read()

    decoded = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            decoded = io.StringIO(raw.decode(encoding))
            break
        except UnicodeDecodeError:
            continue

    if decoded is None:
        raise ValueError("Unable to decode CSV file. Please save it as UTF-8.")

    sample = decoded.getvalue()[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=delimiters)
    except csv.Error:
        dialect = csv.excel
        dialect.delimiter = ";"

    decoded.seek(0)
    reader = csv.DictReader(decoded, dialect=dialect)

    fieldnames = [h.strip() for h in (reader.fieldnames or []) if h and h.strip()]

    if required_columns:
        missing = set(required_columns) - set(fieldnames)
        if missing:
            raise KeyError(f"Missing CSV columns: {', '.join(sorted(missing))}")

    return reader, fieldnames


class ImportButtonHeaderMixin:
    """
    Adds an 'Import CSV / XLSX' action into the header '...' dropdown (if present),
    otherwise adds a normal header button.

    Usage:
        class FooIndexView(ImportButtonHeaderMixin, IndexView):
            import_url_name = "foo_import"
    """
    import_url_name: Optional[str] = None
    import_label = _("Import CSV / XLSX")
    import_icon = "upload"
    import_priority = 80

    def get_header_buttons(self):
        buttons = list(super().get_header_buttons())

        if not self.import_url_name:
            return buttons

        # Match your import view permission basis: user must be able to add
        if not self.permission_policy.user_has_permission(self.request.user, "add"):
            return buttons

        import_btn = Button(
            label=self.import_label,
            url=reverse(self.import_url_name),
            icon_name=self.import_icon,
            priority=self.import_priority,
        )

        # Try to inject into the existing "..." dropdown in header (ButtonWithDropdown)
        for i, btn in enumerate(buttons):
            if isinstance(btn, ButtonWithDropdown):
                existing = None
                for attr in ("buttons", "_buttons", "menu_items", "items", "dropdown_buttons"):
                    if hasattr(btn, attr):
                        existing = list(getattr(btn, attr) or [])
                        break

                # If we can't introspect safely, fall back to separate button
                if existing is None:
                    buttons.append(import_btn)
                    return buttons

                buttons[i] = ButtonWithDropdown(
                    buttons=existing + [import_btn],
                    icon_name=getattr(btn, "icon_name", "dots-horizontal"),
                    attrs=getattr(btn, "attrs", None) or {},
                    priority=getattr(btn, "priority", 100),
                )
                return buttons

        # No dropdown in header -> add as a normal header button
        buttons.append(import_btn)
        return buttons


RowHandler = Callable[[object, dict, int], bool]
# RowHandler must return True if created else False (updated)


def make_snippet_csv_import_view(
    *,
    perm: str,
    template_name: str,
    success_url_name: str,
    required_columns: Iterable[str],
    row_handler: RowHandler,
    import_url_name: str,
):
    """
    Factory that creates a CSV import view for any snippet model.

    - perm: Django permission string, e.g. "utils.add_diasporadirectory"
    - template_name: the upload form template
    - success_url_name: where to redirect after success, usually snippet list
    - required_columns: columns required in CSV
    - row_handler: business logic to validate and create/update the row
    - import_url_name: used for redirecting back to import page on row errors
    """
    @permission_required(perm)
    def view(request):
        if request.method == "POST":
            form = UploadCSVForm(request.POST, request.FILES)
            if form.is_valid():
                f = form.cleaned_data["csv_file"]

                try:
                    reader, _ = read_csv_as_dicts(f, required_columns=required_columns)
                except ValueError as e:
                    messages.error(request, str(e))
                    return redirect(reverse(import_url_name))
                except KeyError as e:
                    messages.error(request, str(e))
                    return redirect(reverse(success_url_name))

                created = 0
                updated = 0

                with transaction.atomic():
                    for line_no, row in enumerate(reader, start=2):
                        try:
                            is_created = bool(row_handler(request, row, line_no))
                        except Exception as e:
                            messages.error(request, str(e))
                            transaction.set_rollback(True)
                            return redirect(reverse(import_url_name))

                        created += int(is_created)
                        updated += int(not is_created)

                messages.success(request, f"Import complete: {created} created, {updated} updated.")
                return redirect(reverse(success_url_name))
        else:
            form = UploadCSVForm()

        return render(request, template_name, {"form": form})

    return view


# ============================================================
# DiasporaDirectory implementation (thin config + row handler)
# ============================================================

ALLOWED_REGIONS = {value for value, _label in REGION_CHOICES}


def diaspora_row_handler(request, row: dict, line_no: int) -> bool:
    """
    DiasporaDirectory-specific validation + upsert.

    Returns True if created, False if updated.
    """
    main_regions = clean(row.get("main_regions") or "")
    if main_regions not in ALLOWED_REGIONS:
        raise ValueError(
            f"Line {line_no}: invalid main_regions '{main_regions}'. "
            f"Allowed values: {', '.join(sorted(ALLOWED_REGIONS))}"
        )

    organisation_name = clean(row.get("organisation_name") or "")
    region = clean(row.get("region") or "")

    if not organisation_name or not main_regions or not region:
        raise ValueError(
            f"Line {line_no}: organisation_name, main_regions, and region must be non-empty."
        )

    defaults = {
        "city": clean(row.get("city") or ""),
        "contact_details": clean(row.get("contact_details") or ""),
        "website": clean(row.get("website") or ""),
        "activity": clean(row.get("activity") or ""),
        "country": clean(row.get("country") or ""),
        "phone_number": clean(row.get("phone_number") or ""),
        "email": clean(row.get("email") or ""),
        "seeking_volunteers": clean(row.get("seeking_volunteers") or "") == "True",
    }

    _obj, is_created = DiasporaDirectory.objects.update_or_create(
        organisation_name=organisation_name,
        main_regions=main_regions,
        region=region,
        defaults=defaults,
    )
    return bool(is_created)


# Create the import view (DiasporaDirectory)
diaspora_directory_import_view = make_snippet_csv_import_view(
    perm="utils.add_diasporadirectory",
    template_name="patterns/snippets/diasporadirectory/diaspora_import.html",
    success_url_name="wagtailsnippets_utils_diasporadirectory:list",
    required_columns=[
        "main_regions",
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
    ],
    row_handler=diaspora_row_handler,
    import_url_name="diaspora_directory_import",
)


class DiasporaDirectoryIndexView(ImportButtonHeaderMixin, IndexView):
    import_url_name = "diaspora_directory_import"
    import_label = _("Import CSV / XLSX")


@register_snippet
class DiasporaDirectorySnippetViewSet(SnippetViewSet):
    model = DiasporaDirectory
    menu_label = "Diaspora directory"
    menu_name = "diaspora_directory"
    icon = "group"
    list_display = ("organisation_name", "main_regions", "city", "region", "country")
    search_fields = (
        "organisation_name",
        "city",
        "region",
        "activity",
        "contact_details",
        "website",
        "country",
        "phone_number",
        "email",
        "seeking_volunteers")

    index_view_class = DiasporaDirectoryIndexView

    # Wagtail-native export
    list_export = (
        "main_regions",
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

    list_filter = (
        "main_regions",
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


# ============================================================
# Admin URLs (registry-style for easy future additions)
# ============================================================

IMPORT_URLS = [
    ("diaspora-directory/import/", diaspora_directory_import_view, "diaspora_directory_import"),
    # Add future snippet imports here, e.g.:
    # ("foo/import/", foo_import_view, "foo_import"),
]


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [path(url, view, name=name) for url, view, name in IMPORT_URLS]

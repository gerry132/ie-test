from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q
from django.http import JsonResponse

from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from irelandie_utils.models import BasePage
from django import forms

from .interactive_tables import get_schema, schema_choices


def humanize_col(col: str) -> str:
    return col.replace("_", " ").strip().title()


def serialize_value(value):
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return value


def serialize_row(obj, columns):
    row = {"id": obj.pk}
    for col in columns:
        row[col] = serialize_value(getattr(obj, col, ""))
    return row


def coerce_filter_value(model, field_name: str, raw: str):
    """
    Convert UI filter values to DB-friendly values.
    Currently handles booleans (Yes/No).
    """
    if raw is None:
        return None

    raw = str(raw).strip()

    try:
        field = model._meta.get_field(field_name)
    except Exception:
        return raw

    # BooleanField / NullBooleanField handling
    if isinstance(field, models.BooleanField):
        lowered = raw.lower()
        if lowered in ("yes", "true", "1"):
            return True
        if lowered in ("no", "false", "0"):
            return False
        # unknown -> return as-is (will error, but that's fine)
        return raw

    return raw


class InteractiveDataTablePageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- schema dropdown ---
        schema_value = (getattr(self.instance, "schema_key", "") or "").strip()

        self.fields["schema_key"] = forms.ChoiceField(
            label=self.fields["schema_key"].label,
            help_text=self.fields["schema_key"].help_text,
            required=False,
            choices=[("", "— Select a table —")] + schema_choices(),
        )
        self.initial["schema_key"] = schema_value

        # If no schema selected yet, keep others empty dropdowns
        if not schema_value:
            empty = [("", "—")]
            for name in ("priority_col_1", "priority_col_2", "filter_col_1", "filter_col_2"):
                old = self.fields[name]
                self.fields[name] = forms.ChoiceField(
                    label=old.label,
                    help_text=old.help_text,
                    required=False,
                    choices=empty,
                )
                self.initial[name] = getattr(self.instance, name, "") or ""
            return
        schema = get_schema(schema_value)
        cols = list(schema.columns)

        col_choices = [(c, humanize_col(c)) for c in cols]
        opt_choices = [("", "— None —")] + col_choices

        # --- priority dropdowns (required after schema is selected; model clean() enforces) ---
        for name in ("priority_col_1", "priority_col_2"):
            old = self.fields[name]
            self.fields[name] = forms.ChoiceField(
                label=old.label,
                help_text=old.help_text,
                required=False,
                choices=col_choices,
            )
            self.initial[name] = getattr(self.instance, name, "") or ""

        # default priority if empty
        if not self.initial["priority_col_1"]:
            self.initial["priority_col_1"] = schema.default_priority[0]
        if not self.initial["priority_col_2"]:
            self.initial["priority_col_2"] = schema.default_priority[1]

        for name in ("filter_col_1", "filter_col_2"):
            old = self.fields[name]
            self.fields[name] = forms.ChoiceField(
                label=old.label,
                help_text=old.help_text,
                required=False,
                choices=opt_choices,
            )
            self.initial[name] = getattr(self.instance, name, "") or ""


class InteractiveDataTablePage(RoutablePageMixin, BasePage):
    """
    Exactly one interactive table per page (by design).
    """

    base_form_class = InteractiveDataTablePageForm
    template = "patterns/pages/irelandie_interactive_tables/irelandie_interactive_tables.html"

    schema_key = models.CharField(max_length=64, blank=True, default="diaspora_directory")

    # Exactly 2 priority columns (single-choice fields)
    priority_col_1 = models.CharField(max_length=64, blank=True, default="")
    priority_col_2 = models.CharField(max_length=64, blank=True, default="")

    # 0–2 filters (single-choice, optional)
    filter_col_1 = models.CharField(max_length=64, blank=True, default="")
    filter_col_2 = models.CharField(max_length=64, blank=True, default="")

    intro = models.TextField(blank=True, default="")

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("schema_key"),
                FieldPanel("priority_col_1"),
                FieldPanel("priority_col_2"),
                FieldPanel("filter_col_1"),
                FieldPanel("filter_col_2"),
            ],
            heading="Interactive table settings",
        ),
    ]

    def clean(self):
        super().clean()

        # Schema is optional, but if blank, page isn't configured yet
        if not self.schema_key:
            return

        schema = get_schema(self.schema_key)
        cols = set(schema.columns)

        # Require both priority columns when schema is selected
        if not self.priority_col_1 or not self.priority_col_2:
            raise ValidationError("Select exactly two priority columns.")

        if self.priority_col_1 not in cols or self.priority_col_2 not in cols:
            raise ValidationError("Priority columns must be valid for the chosen table.")
        if self.priority_col_1 == self.priority_col_2:
            raise ValidationError("Priority columns must be different.")

        # Filters
        for f in (self.filter_col_1, self.filter_col_2):
            if f and f not in cols:
                raise ValidationError(f"Filter column '{f}' is not valid for this table.")
        if self.filter_col_1 and self.filter_col_1 == self.filter_col_2:
            raise ValidationError("Filter columns must be different (or leave one blank).")

    @route(r"^data/$")
    def data_endpoint(self, request):
        if not self.schema_key:
            return JsonResponse({"rows": [], "columns": [], "priority_columns": [], "other_columns": []})

        schema = get_schema(self.schema_key)
        Model = schema.model

        priority_cols = [self.priority_col_1, self.priority_col_2]
        other_cols = [c for c in schema.columns if c not in priority_cols]

        search = (request.GET.get("q") or "").strip()
        f1_name = (request.GET.get("f1_name") or "").strip()
        f1_val = (request.GET.get("f1_val") or "").strip()
        f2_name = (request.GET.get("f2_name") or "").strip()
        f2_val = (request.GET.get("f2_val") or "").strip()

        page_num = int(request.GET.get("page") or 1)
        per_page = min(int(request.GET.get("per_page") or 25), 100)

        qs = Model.objects.all()

        # Debounced search over ALL inferred columns (MVP)
        if search:
            q_obj = Q()
            for col in schema.columns:
                q_obj |= Q(**{f"{col}__icontains": search})
            qs = qs.filter(q_obj)

        # Up to 2 dropdown filters
        if f1_name and f1_val and f1_name in schema.columns:
            qs = qs.filter(**{f1_name: coerce_filter_value(Model, f1_name, f1_val)})

        if f2_name and f2_val and f2_name in schema.columns:
            qs = qs.filter(**{f2_name: coerce_filter_value(Model, f2_name, f2_val)})

        if schema.default_ordering:
            qs = qs.order_by(*schema.default_ordering)

        paginator = Paginator(qs, per_page)
        page = paginator.get_page(page_num)

        rows = [serialize_row(obj, schema.columns) for obj in page.object_list]

        return JsonResponse(
            {
                "schema": schema.key,
                "columns": schema.columns,
                "priority_columns": priority_cols,
                "other_columns": other_cols,
                "rows": rows,
                "pagination": {
                    "page": page.number,
                    "pages": paginator.num_pages,
                    "count": paginator.count,
                    "has_next": page.has_next(),
                    "has_prev": page.has_previous(),
                },
            }
        )

    def get_context(self, request):
        ctx = super().get_context(request)
        if not self.schema_key:
            ctx["configured"] = False
            return ctx

        schema = get_schema(self.schema_key)
        ctx["configured"] = True
        ctx["priority_cols"] = (self.priority_col_1, self.priority_col_2)
        ctx["filter_cols"] = [c for c in (self.filter_col_1, self.filter_col_2) if c]

        # --- Pagination ---
        Model = schema.model
        qs = Model.objects.all()
        page_num = request.GET.get("page") or 1
        per_page = 25
        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page_num)

        rows = [serialize_row(obj, schema.columns) for obj in page_obj.object_list]

        ctx["rows"] = rows
        ctx["page_obj"] = page_obj
        ctx["other_columns"] = [c for c in schema.columns if c not in ctx["priority_cols"]]
        return ctx

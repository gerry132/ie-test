
from dataclasses import dataclass
from typing import Iterable, Type

from django.db import models


def infer_columns(
    model: Type[models.Model],
    *,
    exclude: Iterable[str] = ("id",),
) -> tuple[str, ...]:
    """
    Infer displayable columns from a Django model.

    MVP rules:
    - concrete DB fields only (no reverse relations)
    - skip relations (FK/M2M) for safety (can be extended later)
    """
    cols: list[str] = []
    for f in model._meta.get_fields():
        if not getattr(f, "concrete", False):
            continue
        if getattr(f, "is_relation", False):
            continue

        name = f.name
        if name in exclude:
            continue

        cols.append(name)

    return tuple(cols)


@dataclass(frozen=True)
class TableSchema:
    key: str
    label: str
    model: Type[models.Model]
    default_priority: tuple[str, str]
    default_ordering: tuple[str, ...] = ()
    exclude_columns: tuple[str, ...] = ("id",)

    @property
    def columns(self) -> tuple[str, ...]:
        return infer_columns(self.model, exclude=self.exclude_columns)


SCHEMAS: dict[str, TableSchema] = {}


def register_schema(schema: TableSchema) -> None:
    SCHEMAS[schema.key] = schema


def get_schema(key: str) -> TableSchema:
    return SCHEMAS[key]


def schema_choices() -> list[tuple[str, str]]:
    # stable ordering for admin dropdown
    return sorted([(k, v.label) for k, v in SCHEMAS.items()], key=lambda x: x[1].lower())


def register_interactive_table_schemas() -> None:
    from irelandie_utils.models import DiasporaDirectory

    register_schema(
        TableSchema(
            key="diaspora_directory",
            label="Diaspora directory",
            model=DiasporaDirectory,
            default_priority=("organisation_name", "city"),
            default_ordering=("organisation_name",),
            exclude_columns=("id",),
        )
    )

    # Later, add more schemas like this:
    #
    # from .models import AnotherSnippet
    # register_schema(
    #     TableSchema(
    #         key="another_snippet",
    #         label="Another snippet table",
    #         model=AnotherSnippet,
    #         default_priority=("name", "region"),
    #         default_ordering=("name",),
    #     )
    # )

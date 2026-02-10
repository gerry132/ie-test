````markdown
# How to Add the Next Snippet Import (Minimal Steps)

This section explains how to add **CSV / XLSX import support** to any new Wagtail Snippet using the existing reusable infrastructure.

You only need to do the following steps.

---

## 1. Write a Row Handler

This function defines how **one row** from the CSV is converted into a database record.

```python
def foo_row_handler(request, row, line_no):
    ...
````

* `row` is a normalized `dict` of column → value
* `line_no` is the CSV line number (useful for error messages)
* Raise errors or call `messages.error()` if validation fails

---

## 2. Create the Import View

Use the shared factory to create the import view.

```python
foo_import_view = make_snippet_csv_import_view(
    model=FooModel,
    required_fields=[...],
    row_handler=foo_row_handler,
    success_redirect="wagtailsnippets_app_foomodel:list",
    template_path="patterns/snippets/foomodel/import.html",
)
```

No decoding, delimiter detection, or transaction handling is needed — all of that is already built in.

---

## 3. Create the IndexView

Attach the reusable import button to the snippet header.

```python
class FooIndexView(ImportButtonHeaderMixin, IndexView):
    import_url_name = "foo_import"
```

This automatically adds **“Import CSV / XLSX”** next to **Download CSV / XLSX** in the snippet header.

---

## 4. Set It on the SnippetViewSet

Tell Wagtail to use the custom IndexView.

```python
class FooSnippetViewSet(SnippetViewSet):
    model = FooModel
    index_view_class = FooIndexView
```

---

## 5. Register the Import URL

Append one tuple to the shared `IMPORT_URLS` list.

```python
("foo/import/", foo_import_view, "foo_import")
```

That’s all the wiring required.

---

## ✅ Done

* No template overrides
* No duplicated logic
* No fragile hacks
* Fully reusable across all snippets

Your new snippet now supports **robust CSV / XLSX importing** with a single header button.

```
```

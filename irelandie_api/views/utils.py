from wagtail.models import Page


def get_queryset(year, locale_code, parent_id, model):

    qs = model.objects.live().public()

    if parent_id:
        try:
            parent = Page.objects.only("id").get(id=parent_id)
            qs = qs.child_of(parent)
        except Page.DoesNotExist:
            return model.objects.none()
    if locale_code:
        qs = qs.filter(locale__language_code=locale_code)
    if year and year != "all":
        qs = qs.filter(publication_date__year=year)
    return qs.order_by("-publication_date").specific()

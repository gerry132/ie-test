from wagtail.admin.viewsets.chooser import ChooserViewSet


class CategoryTagViewSet(ChooserViewSet):
    model = "irelandie_tags.TagPage"


tag_chooser_viewset = CategoryTagViewSet("category_tag_chooser")

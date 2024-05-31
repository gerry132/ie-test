from wagtail.admin.viewsets.chooser import ChooserViewSet


class CategoryTagViewSet(ChooserViewSet):
    model = "irelandie_tags.TagPage"
    search_fields = ["title", "locale_id"]


tag_chooser_viewset = CategoryTagViewSet("category_tag_chooser")


class DestinationTagViewSet(ChooserViewSet):
    model = "irelandie_tags.DestinationTagPage"
    search_fields = ["title", "locale_id"]


destination_tag_chooser_viewset = DestinationTagViewSet("destination_tag_chooser")

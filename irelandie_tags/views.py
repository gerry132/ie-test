from wagtail.admin.viewsets.chooser import ChooserViewSet


class CategoryTagViewSet(ChooserViewSet):
    model = "irelandie_tags.TagPage"


tag_chooser_viewset = CategoryTagViewSet("category_tag_chooser")


class DestinationTagViewSet(ChooserViewSet):
    model = "irelandie_tags.DestinationTagPage"


destination_tag_chooser_viewset = DestinationTagViewSet("destination_tag_chooser")

from wagtail.admin.viewsets.chooser import ChooserViewSet


class CategoryTagViewSet(ChooserViewSet):
    # The model can be specified as either the model class or an "app_label.model_name" string;
    # using a string avoids circular imports when accessing the StreamField block class (see below)
    model = "irelandie_tags.TagPage"


tag_chooser_viewset = CategoryTagViewSet("category_tag_chooser")

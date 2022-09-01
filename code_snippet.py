# -*- coding: utf-8 -*-
# # Section features
#
# class AlertBlock(blocks.PageChooserBlock):
#
#     class Meta:
#         label = 'AlertBlock'
#         template = ''
#
#     page_type_classes = [
#         'AlertPage'
#     ]
#
#
# class ContactDetailBlock(blocks.PageChooserBlock):
#
#     class Meta:
#         label = 'ContactDetailBlock'
#         template = ''
#
#     page_type_classes = [
#         'ContactDetailPage'
#     ]
#
#
# class DocumentBlock(DocumentChooserBlock):
#
#     class Meta:
#         label = 'DocumentBlock'
#         template = ''
#
#     pass
#
#
# class ImageBlock(ImageChooserBlock):
#
#     class Meta:
#         label = 'ImageBlock'
#         template = ''
#
#     pass
#
#
# class JumpboxWithImageBlock(blocks.StructBlock):
#
#     class Meta:
#         label = 'JumpboxWithImageBlock'
#         template = ''
#
#     image = ImageChooserBlock()
#     page = blocks.PageChooserBlock(required=False)
#     description = blocks.CharBlock(required=False)
#     text = blocks.CharBlock(required=False)
#     url = blocks.URLBlock(required=False)
#
#
# class JumpboxBlock(blocks.StructBlock):
#
#     class Meta:
#         label = 'JumpboxBlock'
#         template = ''
#
#     page = blocks.PageChooserBlock(required=False)
#     description = blocks.CharBlock(required=False)
#     text = blocks.CharBlock(required=False)
#     url = blocks.URLBlock(required=False)
#
#
# class PersonBlock(blocks.PageChooserBlock):
#
#     class Meta:
#         label = 'PersonBlock'
#         template = ''
#
#     page_type_classes = [
#         'PersonPage'
#     ]
#
#
# class PlaceBlock(blocks.PageChooserBlock):
#
#     class Meta:
#         label = 'PlaceBlock'
#         template = ''
#
#     page_type_classes = [
#         'PlacePage'
#     ]
#
#
# class RichTextBlock(blocks.RichTextBlock):
#
#     class Meta:
#         label = 'RichTextBlock'
#         template = ''
#
#     pass
#
#
# class RoleBlock(blocks.PageChooserBlock):
#
#     class Meta:
#         label = 'RoleBlock'
#         template = ''
#
#     page_type_classes = [
#         'app.RolePage'
#     ]
#
#
# class TableBlock(WagtailTableBlock):
#
#     class Meta:
#         label = 'TableBlock'
#         template = ''
#
#     pass
#
# class YoutubeLinkValue(StructValue):
#
#     def embedding_url(self):
#
#         url = self.get('url', None)
#         if url is None:
#             return None
#
#         if '/embed/' in url:
#             return url
#
#         pattern = r'^(http(s)?:\/\/)?(www\.)?((youtu)(be)?)?'
#         pattern += r'(\.(com)|\.(be))?(\/)(watch\?v=)?|(\&.+)?'
#
#         video_id = re.sub(pattern, '', url)
#         video_id = re.sub(r'(&list.+)|((\s)$)', '', video_id)
#
#         return f'https://www.youtube.com/embed/{video_id}'
#
#
# class YoutubeVideoBlock(blocks.StructBlock):
#
#     class Meta:
#         label = 'YoutubeVideoBlock'
#         value_class = YoutubeLinkValue
#
#     url = blocks.CharBlock()
#
#
# # Sections
#
# class BaseSectionBlock(blocks.StructBlock):
#     title = blocks.CharBlock(required=False)
#     body = blocks.StreamBlock([], required=False)
#
#
# class CorporateInformationPageSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('contact_detail', ContactDetailBlock()),
#             ('document', DocumentBlock()),
#             ('image', ImageBlock()),
#             ('person', PersonBlock()),
#             ('place', PlaceBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#             ('role', RoleBlock()),
#             ('table', TableBlock()),
#         ],
#         required=False
#     )
#
#
# class CampaignSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('contact_detail', ContactDetailBlock()),
#             ('document', DocumentBlock()),
#             ('image', ImageBlock()),
#             ('jumpbox', JumpboxBlock()),
#             ('jumpbox_with_image', JumpboxWithImageBlock()),
#             ('place', PlaceBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#             ('table', TableBlock()),
#             ('youtube_video', YoutubeVideoBlock()),
#         ],
#         required=False
#     )
#
#
# class EventSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('contact_detail', ContactDetailBlock()),
#             ('document', DocumentBlock()),
#             ('image', ImageBlock()),
#             ('place', PlaceBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#             ('table', TableBlock()),
#             ('youtube_video', YoutubeVideoBlock()),
#         ],
#         required=False
#     )
#
#
# class NewsSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('contact_detail', ContactDetailBlock()),
#             ('document', DocumentBlock()),
#             ('image', ImageBlock()),
#             ('place', PlaceBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#             ('table', TableBlock()),
#             ('youtube_video', YoutubeVideoBlock()),
#         ],
#         required=False
#     )
#
#
# class PersonPageSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('contact_detail', ContactDetailBlock()),
#             ('place', PlaceBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#             ('role', RoleBlock()),
#         ],
#         required=False
#     )
#
#
# class PlacePageSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('contact_detail', ContactDetailBlock()),
#             ('document', DocumentBlock()),
#             ('person', PersonBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#             ('role', RoleBlock()),
#             ('table', TableBlock()),
#         ],
#         required=False
#     )
#
#
# class PressReleasePageSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('document', DocumentBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#             ('table', TableBlock()),
#         ],
#         required=False
#     )
#
#
# class PublicationPageSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('document', DocumentBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#             ('table', TableBlock()),
#         ],
#         required=False
#     )
#
#
# class RolePageSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('contact_detail', ContactDetailBlock()),
#             ('person', PersonBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#         ],
#         required=False
#     )
#
#
# class SiteInformationPageSectionBlock(BaseSectionBlock):
#
#     class Meta:
#         label = 'SectionBlock'
#         template = ''
#
#     body = blocks.StreamBlock(
#         [
#             ('document', DocumentBlock()),
#             ('image', ImageBlock()),
#             ('rich_text', RichTextBlock(features=[
#                 'h3', 'blockquote', 'bold', 'link', 'document-link', 'ul'])),
#             ('table', TableBlock()),
#         ],
#         required=False
#     )
#
#
# # Models
#
# ROOT_PAGE = 'MissionPage'
#
#
# # Homepage
#
# class HomepagePage(Page, TranslatableMixin):
#
#     alerts = StreamField(
#         [
#             ('alerts', AlertChooserBlock()),
#         ],
#         blank=True,
#         null=True,
#         max_num=1,
#         min_num=0,
#     )
#
#     jumpboxes = StreamField(
#         [
#             ('jumpbox', JumpboxBlock())
#         ],
#         blank=True,
#         null=True,
#         min_num=0,
#     )
#
#     jumpboxes_with_image = StreamField(
#         [
#             ('jumpbox', JumpboxWithImageBlock())
#         ],
#         blank=True,
#         null=True,
#         min_num=0,
#         max_num=3,
#     )
#
#     max_count = 1
#     subpage_types = [
#         'CountryGroupPageIndex'
#     ]
#
#     content_panels = AbstractHomepagePage.content_panels + [
#         StreamFieldPanel('alerts'),
#         StreamFieldPanel('jumpboxes'),
#         StreamFieldPanel('jumpboxes_with_image'),
#     ]
#
#
# # Indexes
#
# class AlertPageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['AlertPage']
#
#
# class ContactDetailPageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['ContactDetailPage']
#
#
# class CorportateInformationPageIndex(
#         RoutablePageMixin, Page, TranslatableMixin):
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['CorportateInformationPage']
#
#
# class CountryGroupPageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#
#     parent_page_types = ['HomepagePage']
#     subpage_types = ['DestinationPage']
#
#     content_panels = Page.content_panels + [
#         FieldPanel('description'),
#     ]
#
#
# class EventPageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['EventPage']
#
#     content_panels = Page.content_panels + [
#         FieldPanel('description'),
#     ]
#
#
# class NewsPageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['NewsPage']
#
#     content_panels = Page.content_panels + [
#         FieldPanel('description'),
#     ]
#
#
# class PersonPageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['PersonPage']
#
#
# class PlacePageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['PlacePage']
#
#
# class PressReleasePageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['PressReleasePage']
#
#     content_panels = Page.content_panels + [
#         FieldPanel('description'),
#     ]
#
#
# class RolePageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['RolePage']
#
#
# class PublicationPageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['PublicationPage']
#
#     content_panels = Page.content_panels + [
#         FieldPanel('description'),
#     ]
#
#
# class SiteInformationPageIndex(RoutablePageMixin, Page, TranslatableMixin):
#
#     parent_page_types = [ROOT_PAGE]
#     subpage_types = ['SiteInformationPage']
#
#
# # Pages
#
#
# class AlertPage(Page, TranslatableMixin):
#
#     DEFAULT_ALERT_TYPE_CHOICE = ('info', 'Info')
#     ALERT_TYPE_CHOICES = [
#         DEFAULT_CHOICE,
#         ('error', 'Danger'),
#         ('success', 'Success'),
#         ('warning', 'Warning'),
#     ]
#
#     alert_type = models.CharField(
#         max_length=255,
#         choices=ALERT_TYPE_CHOICES,
#         default=DEFAULT_ALERT_TYPE_CHOICE[0]
#     )
#     body = StreamField(
#         [
#             ('richtext', RichTextBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#
#     parent_page_types = ['AlertPageIndex']
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('alert_type'),
#         StreamFieldPanel('body'),
#     ]
#
#
# class ContactDetailPage(Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#
#     address_line_1 = models.CharField(blank=True, null=True)
#     address_line_2 = models.CharField(blank=True, null=True)
#     address_line_3 = models.CharField(blank=True, null=True)
#
#     emails = models.CharField(blank=True, null=True)
#     telephone_numbers = models.CharField(blank=True, null=True)
#     faxes = models.CharField(blank=True, null=True)
#
#     body = StreamField(
#         [
#             ('richtext', RichTextBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         StreamFieldPanel('body'),
#         FieldPanel('description'),
#         FieldPanel('emails'),
#         FieldPanel('telephone_numbers'),
#         FieldPanel('faxes'),
#     ]
#
#
# class CorportateInformationPage(Page, TranslatableMixin):
#
#     body = StreamField(
#         [
#             ('section', CorporateInformationPageSectionBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#     description = models.TextField(blank=True, null=True)
#
#     parent_page_types = ['CorportateInformationPageIndex']
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         StreamFieldPanel('body'),
#     ]
#
#
# class DestinationPage(Page, TranslatableMixin):
#
#     parent_page_types = ['CountryGroupPageIndex']
#     subpage_types = ['MissionPage']
#
#
# class EventPage(Page, TranslatableMixin):
#
#     body = StreamField(
#         [
#             ('section', EventPageSectionBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#     description = models.TextField(blank=True, null=True)
#     date = models.DateTimeField(blank=True, null=True)
#
#     parent_page_types = [
#         'EventPageIndex',
#     ]
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         FieldPanel('description'),
#         StreamFieldPanel('body'),
#         FieldPanel('date'),
#     ]
#
#
# class MissionPage(Page, TranslatableMixin):
#
#     parent_page_types = ['DestinationPage']
#     subpage_types = [
#         'AlertPageIndex',
#         'ContactDetailPageIndex',
#         'CorportateInformationPageIndex',
#         'NewsPageIndex',
#         'PersonPageIndex',
#         'PlacePageIndex',
#         'RolePageIndex',
#         'PublicationPageIndex',
#         'SiteInformationPageIndex',
#     ]
#
#
# class NewsPage(Page, TranslatableMixin):
#
#     body = StreamField(
#         [
#             ('section', NewsPageSectionBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#     description = models.TextField(blank=True, null=True)
#
#     parent_page_types = [
#         'NewsPageIndex',
#     ]
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         StreamFieldPanel('body'),
#         FieldPanel('description'),
#     ]
#
#
# class PersonPage(Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#     body = StreamField(
#         [
#             ('section', PersonPageSectionBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#     image = models.ForeignKey(
#         'wagtailimages.Image',
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='+'
#     )
#
#     parent_page_types = [
#         'PersonPageIndex',
#     ]
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         FieldPanel('description'),
#         StreamFieldPanel('body'),
#         ImageChooserPanel('image'),
#     ]
#
#
# class PlacePage(Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#     body = StreamField(
#         [
#             ('section', PlacePageSectionBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#
#     address_line_1 = models.CharField(max_length=255, blank=True, null=True)
#     address_line_2 = models.CharField(max_length=255, blank=True, null=True)
#     address_line_3 = models.CharField(max_length=255, blank=True, null=True)
#
#     emails = models.CharField(max_length=255, blank=True, null=True)
#     telephone_numbers = models.CharField(
#         max_length=255, blank=True, null=True)
#     faxes = models.CharField(max_length=255, blank=True, null=True)
#
#     latitude = models.CharField(max_length=255, blank=True, null=True)
#     longtitude = models.CharField(max_length=255, blank=True, null=True)
#
#     opening_hours_monday_from = models.TimeField(blank=True, null=True)
#     opening_hours_monday_to = models.TimeField(blank=True, null=True)
#     opening_hours_tuesday_from = models.TimeField(blank=True, null=True)
#     opening_hours_tuesday_to = models.TimeField(blank=True, null=True)
#     opening_hours_wednesday_from = models.TimeField(blank=True, null=True)
#     opening_hours_wednesday_to = models.TimeField(blank=True, null=True)
#     opening_hours_thursday_from = models.TimeField(blank=True, null=True)
#     opening_hours_thursday_to = models.TimeField(blank=True, null=True)
#     opening_hours_friday_from = models.TimeField(blank=True, null=True)
#     opening_hours_friday_to = models.TimeField(blank=True, null=True)
#     opening_hours_saturday_from = models.TimeField(blank=True, null=True)
#     opening_hours_saturday_to = models.TimeField(blank=True, null=True)
#     opening_hours_sunday_from = models.TimeField(blank=True, null=True)
#     opening_hours_sunday_to = models.TimeField(blank=True, null=True)
#
#     parent_page_types = [
#         'PlacePageIndex',
#     ]
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         FieldPanel('description'),
#         StreamFieldPanel('body'),
#         FieldPanel('latitude'),
#         FieldPanel('longtitude'),
#         FieldPanel('emails'),
#         FieldPanel('telephone_numbers'),
#         FieldPanel('faxes'),
#         FieldPanel('opening_hours_monday_from'),
#         FieldPanel('opening_hours_monday_to'),
#         FieldPanel('opening_hours_tuesday_from'),
#         FieldPanel('opening_hours_tuesday_to'),
#         FieldPanel('opening_hours_wednesday_from'),
#         FieldPanel('opening_hours_wednesday_to'),
#         FieldPanel('opening_hours_thursday_from'),
#         FieldPanel('opening_hours_thursday_to'),
#         FieldPanel('opening_hours_friday_from'),
#         FieldPanel('opening_hours_friday_to'),
#         FieldPanel('opening_hours_saturday_from'),
#         FieldPanel('opening_hours_saturday_to'),
#         FieldPanel('opening_hours_sunday_from'),
#         FieldPanel('opening_hours_sunday_to'),
#     ]
#
#
# class PressReleasePage(Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#     body = StreamField(
#         [
#             ('section', PressReleasePageSectionBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#
#     parent_page_types = [
#         'PressReleasePageIndex',
#     ]
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         FieldPanel('description'),
#         StreamFieldPanel('body'),
#     ]
#
#
# class PublicationPage(Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#     body = StreamField(
#         [
#             ('section', PublicationPageSectionBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#
#     parent_page_types = [
#         'PublicationPageIndex',
#     ]
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         FieldPanel('description'),
#         StreamFieldPanel('body'),
#     ]
#
#
# class RolePage(Page, TranslatableMixin):
#
#     PERSON_PAGE_MODEL = PersonPage
#
#     description = models.TextField(blank=True, null=True)
#     body = StreamField(
#         [
#             ('section', RolePageSectionBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#     role_holder = models.ForeignKey(
#         PERSON_PAGE_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='+',
#     )
#
#     parent_page_types = [
#         'RolePageIndex',
#     ]
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         FieldPanel('description'),
#         StreamFieldPanel('body'),
#         PageChooserPanel('role_holder'),
#     ]
#
#
# class SiteInformationPage(Page, TranslatableMixin):
#
#     description = models.TextField(blank=True, null=True)
#     body = StreamField(
#         [
#             ('section', SiteInformationPageSectionBlock()),
#         ],
#         blank=True,
#         null=True
#     )
#
#     parent_page_types = [
#         'SiteInformationPageIndex',
#     ]
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         FieldPanel('first_published_at'),
#         FieldPanel('description'),
#         StreamFieldPanel('body'),
#     ]

# -*- coding: utf-8 -*-
from django.db import models
from django.utils.functional import cached_property
from wagtail.admin.panels import InlinePanel, FieldPanel, TabbedInterface, ObjectList, MultiFieldPanel, HelpPanel
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks as wagtail_blocks
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from wagtail.images import get_image_model_string


from irelandie_home.blocks import SecondaryCallToAction
from irelandie_home.models import HomePage
from irelandie_navigation.blocks import LinkBlock, NoticeBarWithMessageLink
from irelandie_pages.models import FreeFormPageBase
from irelandie_news.models import NewsPage
from irelandie_utils import blocks
from irelandie_utils.blocks import HomepageFeatureBlock
from irelandie_utils.utils import get_root_info
from irelandie_utils.models import BasePage, CountryGroup, HeroPage, SocialFields, ListingFields
from wagtail.snippets.blocks import SnippetChooserBlock
from django.forms import ValidationError

from django.dispatch import receiver
from django.db.models.signals import pre_delete

from wagtail.signals import page_published
from wagtail.contrib.frontend_cache.utils import PurgeBatch


class CountryGroupPageIndex(BasePage):
    template = "irelandie_assets/pages/countries.html"

    description = models.TextField(blank=True)
    override_primary_navigation = StreamField(
        [("link", LinkBlock())], blank=True, help_text="Override the site navigation"
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
    ]
    settings_panels = BasePage.settings_panels + [
        FieldPanel("override_primary_navigation")
    ]


class DestinationPage(HeroPage):
    template = "patterns/pages/missions/country_page.html"

    five_panel_block = StreamField(
        [
            ("five_panel_block", HomepageFeatureBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    stories = StreamField(
        [
            ("story", blocks.StoryBlock()),
        ],
        blank=True,
        null=True,
    )

    region = models.ForeignKey(
        CountryGroup,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
    )

    logo_cards = StreamField(
        [("logo_cards", blocks.LogoCardsBlock())],
        blank=True,
        max_num=1,
    )

    body = StreamField(
        [
            ("homepage_feature", blocks.HomepageFeatureImageVideoBlock()),
            ("advanced_rich_text_snippet", blocks.AdvancedRichtextSnippetBlock()),
            ("two_column_feature", blocks.StoryBlock()),
            ("rich_text_advanced", blocks.AdvancedRichTextBlock()),
            ("youtube_video", blocks.YoutubeVideoBlock()),
            ("video", blocks.CustomVideoChooserBlockAlt()),
            ("link_cards", blocks.LinkCardsBlock()),
            ("Featured_tagged_stories", blocks.FeaturedTaggedStoriesBlock()),
            ("logo_cards", blocks.LogoCardsBlock()),
            ("html", wagtail_blocks.RawHTMLBlock(
                help_text="Add title attribute value to iframe for accessibility.",
                template="patterns/molecules/streamfield/blocks/raw_html_block.html",
            )),
            ("stats_block", blocks.StatsBlock()),
            ("multimedia_row", blocks.MultimediaRowBlock()),
            ("image", blocks.ImageBlock()),
            ("document", blocks.DocumentBlock()),
            ("wide_feature", blocks.WideFeatureBlock()),
            ("overview_pull_out_textblock", blocks.OverviewPullOutTextBlock()),
            ("info_at_a_glance", blocks.InfoAtAGlanceBlock()),
            ("policy_document_box", blocks.PolicyDocumentBoxBlock()),
            ("story_photo_gallery", blocks.StoryPhotoGalleriesBlock()),
            ("timeline_photo_gallery", blocks.TimelinePhotoGalleriesBlock()),
            (
                "pinned_story",
                wagtail_blocks.StructBlock(
                    [
                        ("pinned_story_hero", blocks.PinnedStoryHeroBlock()),
                    ],
                    template="patterns/molecules/pinned-stories/pinned_stories.html",
                ),
            ),
        ],
        block_counts={
            "pinned_story": {"max_num": 1},
        },
        blank=True,
        null=True,
    )
    body1 = StreamField(
        [
            ("homepage_feature", blocks.HomepageFeatureImageVideoBlock()),
            ("advanced_rich_text_snippet", blocks.AdvancedRichtextSnippetBlock()),
            ("two_column_feature", blocks.StoryBlock()),
            ("rich_text_advanced", blocks.AdvancedRichTextBlock()),
            ("youtube_video", blocks.YoutubeVideoBlock()),
            ("video", blocks.CustomVideoChooserBlockAlt()),
            ("link_cards", blocks.LinkCardsBlock()),
            ("Featured_tagged_stories", blocks.FeaturedTaggedStoriesBlock()),
            ("logo_cards", blocks.LogoCardsBlock()),
            ("html", wagtail_blocks.RawHTMLBlock(
                help_text="Add title attribute value to iframe for accessibility.",
                template="patterns/molecules/streamfield/blocks/raw_html_block.html",
            )),
            ("image", blocks.ImageBlock()),
            ("document", blocks.DocumentBlock()),
            ("wide_feature", blocks.WideFeatureBlock()),
            ("overview_pull_out_textblock", blocks.OverviewPullOutTextBlock()),
            ("info_at_a_glance", blocks.InfoAtAGlanceBlock()),
            ("policy_document_box", blocks.PolicyDocumentBoxBlock()),
            ("story_photo_gallery", blocks.StoryPhotoGalleriesBlock()),
            ("timeline_photo_gallery", blocks.TimelinePhotoGalleriesBlock()),
            ("stats_block", blocks.StatsBlock()),
            ("multimedia_row", blocks.MultimediaRowBlock()),
        ],
        blank=True,
        null=True,
    )
    beta_element = models.ForeignKey(
        'utils.BetaSnippet',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = ([FieldPanel("five_panel_block", heading="5 Panel Block")] +
                      HeroPage.content_panels + [
                          FieldPanel("region"),
                          FieldPanel("body1", heading="Body"),
                          FieldPanel("stories", heading="Two Column Feature"),
                          FieldPanel("logo_cards", heading="Logo Cards"),
                          FieldPanel("body"),
                      ])

    settings_panels = (
        [
            FieldPanel("beta_element", permission="access_admin"),
        ] +
        HeroPage.settings_panels

    )

    @cached_property
    def related_articles(self):
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                m = MissionPage.objects.live().get(id=p.id)
                if m.root_page:
                    return (
                        NewsPage.objects
                        .filter(locale=self.locale,
                                related_articles_active=True)
                        .public()
                        .live()
                        .order_by("-publication_date")[:4]
                        .specific()
                    )
        return None

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        pages = self.get_ancestors()

        context, root_found = get_root_info(context, pages)
        if not root_found:
            f = HomePage.objects.all()[:1].get()
            context['default_image'] = f.default_image
        return context

    def clean(self):
        if self.hero_image and self.five_panel_block or self.hero_video and self.five_panel_block:
            raise ValidationError(
                {
                    "five_panel_block": ValidationError(
                        "Choose only a five_panel_block or a hero image/video"
                    ),
                    "hero_image": ValidationError(
                        "Choose only a five_panel_block or a hero image/video"
                    ),
                }
            )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel_with_size, heading='Hero'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])


IMAGE_MODEL = get_image_model_string()


class JobContentPage(BasePage):
    template = "patterns/pages/irelandie_job/job.html"
    subtitle = models.CharField(max_length=100,
                                null=True,
                                blank=True)
    body = StreamField(
        [
            ("rich_text", blocks.AdvancedRichTextBlock()),
            ("document", blocks.DocumentBlock()),
        ],
        blank=True,
    )
    job_index_page_summary = models.TextField(
        max_length=300,
        help_text="A brief 1-2 sentence job summary. This will appear on the job opportunities index page, not on the "
                  "job posting itself.",
        null=True
    )
    privacy_policy = models.ForeignKey(
        'utils.PrivacyPolicySnippet',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("subtitle", permission="access_admin"),
        MultiFieldPanel(
            [
                HelpPanel(content='help_text', template='patterns/molecules/streamfield/'
                                                        'help_text_scheduled_publishing.html', heading='',
                          classname=''),
                FieldPanel('go_live_at'),
                FieldPanel('expire_at'),
            ],
            heading="Scheduled publishing", help_text="The expiry date you select will unpublish the job advert on "
                                                      "the selected date. It will also automatically output the "
                                                      "selected date as the 'Closing date:' on the published job "
                                                      "advert. "
        ),
        FieldPanel("job_index_page_summary"),
        FieldPanel("body"),
        FieldPanel("privacy_policy", permission="access_admin"),
    ]
    COMMON_PROMOTE_PANELS = (
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
    )

    promote_panels = (
        [
            MultiFieldPanel(COMMON_PROMOTE_PANELS, heading="For search engines"),
            FieldPanel('show_in_menus'),
        ] +
        SocialFields.promote_panels +
        ListingFields.promote_panels
    )

    settings_panels = ([
                           MultiFieldPanel(
                               [
                                   FieldPanel("custom_header", permission="access_admin"),
                                   FieldPanel("custom_footer", permission="access_admin")
                               ],
                               "Root Navigation"
                           ),
                       ] +
                       BasePage.webchat_panel
                       )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        parent = self.get_parent()
        if parent.content_type.name == "job index page":
            context['privacy_policy_parent'] = self.get_parent().specific.privacy_policy
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = MissionPage.objects.live().get(id=p.id)
                if missions.root_page:
                    context['mission_web_bot'] = missions.web_bot_script
        return context


class JobIndexPage(BasePage):
    subpage_types = [
        'JobContentPage',
    ]
    template = "patterns/pages/irelandie_job/job_index.html"
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    privacy_policy = models.ForeignKey(
        'utils.PrivacyPolicySnippet',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("privacy_policy", permission="access_admin"),
    ]

    @cached_property
    def related_jobs(self):
        return (
            JobContentPage.objects
            .child_of(self)
            .filter(locale=self.locale)
            .public()
            .live()
            .order_by("-first_published_at")
            .specific()
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = MissionPage.objects.live().get(id=p.id)
                if missions.root_page:
                    context['mission_web_bot'] = missions.web_bot_script
        return context


def job_page_changed(job_page):
    # Find all the live JobIndexPages that contain this jpb_page
    batch = PurgeBatch()
    for job_index in JobIndexPage.objects.live():
        if job_page in job_index.related_jobs().object_list:
            batch.add_page(job_index)

    # Purge all the job indexes we found in a single request
    batch.purge()


@receiver(page_published, sender=JobContentPage)
def job_published_handler(instance, **kwargs):
    job_page_changed(instance)


@receiver(pre_delete, sender=JobContentPage)
def job_deleted_handler(instance, **kwargs):
    job_page_changed(instance)


class MissionPage(HeroPage):
    template = "patterns/pages/irelandie_missions/mission.html"
    search_bar = models.BooleanField(default=False)
    popular_pages = StreamField(
        [("link", LinkBlock())], blank=True, help_text="Add pages to hero search."
    )
    root_page = models.BooleanField(default=True)
    favicon = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    notice_bar = StreamField(
        [
            ("noticebar", NoticeBarWithMessageLink()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    stories = StreamField(
        [
            ("story", blocks.StoryBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
    )
    top_body = StreamField(
        [
            ("advanced_rich_text", blocks.AdvancedRichTextBlock()),
            ("link_cards", blocks.LinkCardsBlock()),
            ("articles", blocks.ArticleCardsBlock()),
            ("logo_cards", blocks.LogoCardsBlock()),
            ("wide_feature_block", blocks.WideFeatureBlock()),
            (
                "pinned_story",
                wagtail_blocks.StructBlock(
                    [
                        ("pinned_story_hero", blocks.PinnedStoryHeroBlock()),
                    ],
                    template="patterns/molecules/pinned-stories/pinned_stories.html",
                ),
            ),
        ],
        block_counts={
            "pinned_story": {"max_num": 1},
        },
        blank=True,
        null=True
    )
    body = StreamField(
        [
            ("two_column_feature", blocks.StoryBlock()),
            ("stats_block", blocks.StatsBlock())
        ],
        blank=True,
        null=True
    )

    person = StreamField(
        [
            ("person", blocks.PersonSocialBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    default_image = StreamField(
        [
            ("default_image", blocks.ImageBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    beta_element = models.ForeignKey(
        'utils.BetaSnippet',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = HeroPage.content_panels + [
        MultiFieldPanel([
            FieldPanel("search_bar", permission="access_admin"),
            FieldPanel("popular_pages", permission="access_admin"),
        ], heading="Searchbar settings",
        ),
        MultiFieldPanel([
            FieldPanel("notice_bar"),
        ], heading="Noticebar settings"
        ),
        FieldPanel("stories", heading="Two Column Feature"),
        FieldPanel("top_body"),
        FieldPanel("person", heading="Person + Social Feed"),
        FieldPanel("body"),
    ]

    @cached_property
    def related_articles(self):
        return (
            NewsPage.objects
            .descendant_of(self)
            .filter(locale=self.locale,
                    featured_home=True)
            .public()
            .live()
            .order_by("-publication_date")[:4]
            .specific()
        )

    settings_panels = (
        [
            FieldPanel("root_page", permission="access_admin"),
            FieldPanel("favicon", permission="access_admin"),
            FieldPanel("beta_element", permission="access_admin"),
            FieldPanel("default_image", permission="access_admin"),
        ] +
        HeroPage.settings_panels

    )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel, heading='Hero'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
    ])

    def save(self, *args, **kwargs):

        key = make_template_fragment_key("mission_page_" + str(self.id))
        cache.delete(key)

        return super().save(*args, **kwargs)


class Magazine(HeroPage):
    template = "irelandie_assets/pages/magazine.html"
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
    )
    body = StreamField(
        [
            ("rich_text", blocks.AdvancedRichTextBlock()),
            ("link_card", blocks.LinkCardsBlock())
        ],
        blank=True,
    )

    content_panels = HeroPage.content_panels + [
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("body")
    ]
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = MissionPage.objects.live().get(id=p.id)
                if missions.root_page:
                    context['mission_web_bot'] = missions.web_bot_script
        return context


class ServiceContent(BasePage):
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    related_content = StreamField(
        [
            ("related_item", blocks.RelatedContentBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
    )
    template = "patterns/pages/toc/table_of_contents.html"
    introduction = RichTextField(blank=True)
    notice_bar_services = StreamField(
        [
            ("noticebar", NoticeBarWithMessageLink()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    stories_top = StreamField(
        [
            ("story", blocks.StoryBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
    )
    stories_bottom = StreamField(
        [
            ("story", blocks.StoryBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
    )
    admin_body1 = StreamField(
        [
            ("admin_contents", blocks.TocAdminBlock())
        ],
        blank=True
    )
    body = StreamField(
        [
            ("content", blocks.TocBlock())
        ],
        blank=True
    )
    admin_body2 = StreamField(
        [
            ("admin_content", blocks.TocAdminBlock())
        ],
        blank=True
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        pages = self.get_ancestors()
        context, root_found = get_root_info(context, pages)
        if not root_found:
            f = HomePage.objects.all()[:1].get()
            context['default_image'] = f.default_image
        return context

    content_panels = BasePage.content_panels + [
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("introduction"),
        MultiFieldPanel([
            FieldPanel("notice_bar_services"),
        ], heading="Noticebar settings"
        ),
        FieldPanel("stories_top", heading="Two Column Feature"),
        FieldPanel("admin_body1", permission="access_admin", heading="Admin_body"),
        FieldPanel("body"),
        FieldPanel("admin_body2", permission="access_admin", heading="Admin_body"),
        FieldPanel("stories_bottom", heading="Two Column"),
        FieldPanel("related_content"),
    ]


class NoticePage(BasePage):
    template = "patterns/pages/missions/notice_page.html"
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    related_content = StreamField(
        [
            ("related_item", blocks.RelatedContentBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
    )
    introduction = RichTextField(blank=True)

    stories_top = StreamField(
        [
            ("story", blocks.StoryBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
    )
    stories_bottom = StreamField(
        [
            ("story", blocks.StoryBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
    )
    admin_body1 = StreamField(
        [
            ("admin_contents", blocks.TocAdminBlock())
        ],
        blank=True
    )
    body = StreamField(
        [
            ("content", blocks.TocBlock())
        ],
        blank=True
    )
    admin_body2 = StreamField(
        [
            ("admin_content", blocks.TocAdminBlock())
        ],
        blank=True
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        pages = self.get_ancestors()
        context, root_found = get_root_info(context, pages)
        if not root_found:
            f = HomePage.objects.all()[:1].get()
            context['default_image'] = f.default_image
        return context

    content_panels = BasePage.content_panels + [
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("introduction"),
        FieldPanel("stories_top", heading="Two Column Feature"),
        FieldPanel("admin_body1", permission="access_admin", heading="Admin_body"),
        FieldPanel("body"),
        FieldPanel("admin_body2", permission="access_admin", heading="Admin_body"),
        FieldPanel("stories_bottom", heading="Two Column"),
        FieldPanel("related_content"),
    ]

    class Meta:
        verbose_name = "Notice"
        verbose_name_plural = "Notice"


class ServicesLandingPage(BasePage):
    template = "patterns/pages/missions/services_landing_page.html"
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    notice_bar_services = StreamField(
        [
            ("noticebar", NoticeBarWithMessageLink()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    rich_text = StreamField(
        [
            ("rich_text", blocks.AdvancedRichTextBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    body = StreamField(
        [
            ("link_box", blocks.LinkBoxesBlock())
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    additional_rich_text = StreamField(
        [
            ("additional_rich_text", blocks.AdvancedRichTextBlock()),
        ],
        blank=True,
        null=True,
    )
    related_content = StreamField(
        [
            ("related_item", blocks.RelatedContentBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        pages = self.get_ancestors()
        context, root_found = get_root_info(context, pages)
        if not root_found:
            f = HomePage.objects.all()[:1].get()
            context['default_image'] = f.default_image
        return context

    content_panels = BasePage.content_panels + [
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("notice_bar_services", heading="Noticebar settings"),
        FieldPanel("rich_text", heading="Advanced Richtext", permission="access_admin"),
        FieldPanel("body", permission="access_admin"),
        FieldPanel("additional_rich_text", heading="Advanced Richtext", permission="access_admin"),
        FieldPanel("related_content"),
    ]


class MissionSearchPage(BasePage):
    template = "patterns/pages/missions/mission_search_page.html"

    description = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
    ]

    """
    Using the descendant_of page filter to only return country pages
    that have been created for a particular language home page.
    Mission page can only be created under the HomePage
    """

    @cached_property
    def regions(self):
        country_groups = CountryGroup.objects.all()
        regions = []

        for group in country_groups:
            countries_count = (
                DestinationPage.objects.descendant_of(self.get_parent())
                .filter(region=group)
                .count()
            )
            if countries_count:
                regions.append(group)

        return regions

    @cached_property
    def countries(self):
        return DestinationPage.objects.descendant_of(self.get_parent())

    def get_context(self, request):
        context = super().get_context(request)
        context["regions"] = self.regions
        context["countries"] = self.countries
        return context


class ConsulatePage(FreeFormPageBase):
    template = "patterns/pages/missions/consulate_page.html"

    body = StreamField(blocks.FreeFormBlocksBase(), blank=True)

    parent_page_types = [
        "irelandie_missions.DestinationPage",
        "irelandie_pages.FreeFormPage",
    ]

    secondary_call_to_action = StreamField(
        [
            ("call_to_action", SecondaryCallToAction()),
        ],
        blank=True,
    )

    twitter_title = models.CharField(max_length=50, blank=True)

    twitter_feed = models.ForeignKey(
        "utils.TwitterEmbed",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )

    content_panels = FreeFormPageBase.content_panels + [
        MultiFieldPanel([
            FieldPanel("twitter_title"),
            FieldPanel("twitter_feed"),
        ], heading="Twitter feed"),
    ]

    secondary_cta_panel = [
        FieldPanel("secondary_call_to_action")
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(FreeFormPageBase.hero_panel, heading='Hero'),
        ObjectList(secondary_cta_panel, heading='Call To Action'),
        ObjectList(FreeFormPageBase.promote_panels, heading='Promote'),
        ObjectList(FreeFormPageBase.settings_panels, heading='Settings', classname="settings"),
    ])

    class Meta:
        verbose_name = "Consulate Page"


class EmbassyPage(FreeFormPageBase):
    template = "patterns/pages/missions/embassy_page.html"

    body = StreamField(blocks.FreeFormBlocksBase(), blank=True)

    parent_page_types = [
        "irelandie_missions.DestinationPage",
        "irelandie_pages.FreeFormPage",
    ]

    secondary_call_to_action = StreamField(
        [
            ("call_to_action", SecondaryCallToAction()),
        ],
        blank=True,
    )

    twitter_title = models.CharField(max_length=50, blank=True)

    twitter_feed = models.ForeignKey(
        "utils.TwitterEmbed",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )

    content_panels = FreeFormPageBase.content_panels + [
        MultiFieldPanel([
            FieldPanel("twitter_title"),
            FieldPanel("twitter_feed"),
        ], heading="Twitter feed"),
    ]

    secondary_cta_panel = [
        FieldPanel("secondary_call_to_action")
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(FreeFormPageBase.hero_panel, heading='Hero'),
        ObjectList(secondary_cta_panel, heading='Call To Action'),
        ObjectList(FreeFormPageBase.promote_panels, heading='Promote'),
        ObjectList(FreeFormPageBase.settings_panels, heading='Settings', classname="settings"),
    ])

    class Meta:
        verbose_name = "Embassy Page"


class EmbassyIndexPage(BasePage):
    template = "patterns/pages/missions/embassy_index_page.html"
    subtitle = StreamField(
        [
            ('subtitle', blocks.AdvancedRichTextBlock()),
            ("embassy_snippet", SnippetChooserBlock(target_model="utils.EmbassySnippet"))
        ],
        null=True,
        blank=False
    )
    body = StreamField(
        [
            ("accordions", blocks.AccordionEmbassyBlock(label="Accordion Block"))],
        blank=True,
        null=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]

    def save(self, *args, **kwargs):

        key = make_template_fragment_key("embassy_index")
        cache.delete(key)

        return super().save(*args, **kwargs)


class GeneralContentPage(HeroPage):
    template = "patterns/pages/missions/general_content_page.html"
    subtitle = models.TextField(blank=True)
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    introduction = models.TextField(blank=True)
    body = StreamField(blocks.GeneralContentBlocks(), blank=True)

    content_panels = HeroPage.content_panels + [
        FieldPanel("subtitle", help_text="Please include a brief description of this page/article. This will not "
                                         "appear live on the page, but will appear publicly as a subtitle in other "
                                         "areas of the site that link to this page."),
        FieldPanel("generic_hero", heading="Mini Hero Block"),
        FieldPanel("introduction"),
        FieldPanel("body"),
        InlinePanel('page_related_tags', label="Related category tags"),
        InlinePanel('page_related_destination_tags', label="Related destination"),

    ]
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from irelandie_utils.templatetags.util_tags import get_tag_links
        from irelandie_utils.templatetags.util_tags import get_destination_tag_links
        destination_tags = self.related_destination_tags
        context["destination_tag_links"] = get_destination_tag_links(destination_tags)
        tag = self.related_tags
        tagging_links = get_tag_links(tag, self)[0]
        tags_no_links = get_tag_links(tag, self)[1]
        context["tagging_links"] = tagging_links
        context["tags_no_links"] = tags_no_links
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = MissionPage.objects.live().get(id=p.id)
                if missions.root_page:
                    context['mission_web_bot'] = missions.web_bot_script
        return context


class GeneralContentIrishAid(HeroPage):
    template = "patterns/pages/missions/general_content_page.html"
    subtitle = models.TextField(blank=True)
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    banner_hero_image = StreamField(
        [
            ("banner_hero_image", blocks.BannerImageBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    introduction = models.TextField(blank=True)
    body = StreamField(blocks.GeneralContentBlocks(), blank=True)

    content_panels = HeroPage.content_panels + [
        FieldPanel("subtitle", help_text="Please include a brief description of this page/article. This will not "
                                         "appear live on the page, but will appear publicly as a subtitle in other "
                                         "areas of the site that link to this page."),
        FieldPanel("generic_hero", heading="Mini Hero Block"),
        FieldPanel("banner_hero_image", heading="Banner Hero Image Block"),
        FieldPanel("introduction"),
        FieldPanel("body"),
        InlinePanel('page_related_tags', label="Related category tags"),
        InlinePanel('page_related_destination_tags', label="Related destination"),

    ]
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from irelandie_utils.templatetags.util_tags import get_tag_links
        from irelandie_utils.templatetags.util_tags import get_destination_tag_links
        destination_tags = self.related_destination_tags
        context["destination_tag_links"] = get_destination_tag_links(destination_tags)
        tag = self.related_tags
        tagging_links = get_tag_links(tag, self)[0]
        tags_no_links = get_tag_links(tag, self)[1]
        context["tagging_links"] = tagging_links
        context["tags_no_links"] = tags_no_links
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = MissionPage.objects.live().get(id=p.id)
                if missions.root_page:
                    context['mission_web_bot'] = missions.web_bot_script
        return context

    def clean(self):
        if self.generic_hero and self.banner_hero_image:
            raise ValidationError(
                "You can't choose both an Mini hero block and a Banner hero image block for the hero media. "
                "Choose a Mini hero block or a Banner hero image block"
            )

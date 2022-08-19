# -*- coding: utf-8 -*-
from django.db import models
from django.utils.functional import cached_property
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, TabbedInterface, ObjectList, MultiFieldPanel
from wagtail.core.fields import StreamField, RichTextField
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from irelandie_home.blocks import SecondaryCallToAction
from irelandie_navigation.blocks import LinkBlock
from irelandie_pages.models import FreeFormPageBase
from irelandie_utils import blocks
from irelandie_utils.blocks import PersonLinkBlock, CustomVideoChooserBlockAlt
from irelandie_utils.models import BasePage, CountryGroup, HeroPage


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
        StreamFieldPanel("override_primary_navigation")
    ]


class CountryPage(HeroPage):
    template = "patterns/pages/missions/country_page.html"

    stories = StreamField(
        [
            ("story", blocks.StoryBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    embeds = StreamField(
        [
            ("youtube", blocks.YoutubeVideoBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    featured_stories = StreamField(
        [
            ("featured_story", blocks.FeaturedStoryBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    featured_embassies = StreamField(
        [
            ("embassy_story", blocks.EmbassyStory()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    region = models.ForeignKey(
        CountryGroup,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
    )

    twitter_title = models.CharField(max_length=50, blank=True)

    twitter_feed = models.ForeignKey(
        "utils.TwitterEmbed",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )

    logo_cards = StreamField(
        [("logo_cards", blocks.LogoCardsBlock())],
        blank=True,
        max_num=1,
    )

    content_panels = HeroPage.content_panels + [
        SnippetChooserPanel("region"),
        StreamFieldPanel("stories"),
        StreamFieldPanel("embeds"),
        StreamFieldPanel("featured_stories"),
        StreamFieldPanel("featured_embassies"),
        StreamFieldPanel("logo_cards", heading="Logo Cards"),
        MultiFieldPanel([
            FieldPanel("twitter_title"),
            SnippetChooserPanel("twitter_feed"),
        ], heading="Twitter feed"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel, heading='Hero'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])


IMAGE_MODEL = get_image_model_string()


class MissionPage(BasePage):
    template = "patterns/pages/irelandie_missions/mission.html"

    name = models.CharField(max_length=255, blank=True)
    person_title = models.CharField(max_length=255, blank=True)
    image = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    video = StreamField(
        [
            ("video", CustomVideoChooserBlockAlt()),
        ],
        blank=True,
    )
    embassy_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    social_media_link = models.URLField(blank=True)
    social_media_text = models.CharField(
        max_length=255, blank=True, default="Connect with person on this social media"
    )
    address = RichTextField(blank=True)
    telephone = models.CharField(max_length=255, blank=True)
    opening_hours = RichTextField(blank=True)
    closure_dates = RichTextField(blank=True)
    emergency_contact_details = RichTextField(blank=True)
    our_services_url = models.URLField(blank=True)
    our_role_url = models.URLField(blank=True)

    alignment = models.CharField(
        choices=(("left", "Left"), ("right", "Right")), max_length=255, default="left"
    )
    background = models.CharField(
        choices=(("light", "Light"), ("dark", "Dark")), max_length=255, default="light"
    )
    links = StreamField(
        [
            ("link", PersonLinkBlock(min_num=0, max_num=6)),
        ],
        blank=True,
    )

    twitter_title = models.CharField(max_length=50, blank=True)
    twitter_username = models.CharField(
        max_length=100,
        blank=True,
        help_text="Twitter username",
    )

    social_url = models.URLField(
        blank=True,
        max_length=255,
        null=True,
        help_text="URL for logo click."
    )
    social_link_text = models.CharField(max_length=50, blank=True)
    social_logo = models.ForeignKey(
        IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel([
            FieldPanel("name", classname="full title"),
            FieldPanel("person_title"),
            FieldPanel("alignment"),
            ImageChooserPanel("image"),
            StreamFieldPanel("video"),
            ImageChooserPanel("embassy_logo"),
            FieldPanel("background"),
            FieldPanel("social_media_link"),
            FieldPanel("social_media_text"),
            FieldPanel("address"),
            FieldPanel("telephone"),
            FieldPanel("opening_hours"),
            FieldPanel("closure_dates"),
            FieldPanel("emergency_contact_details"),
            StreamFieldPanel("links"),
        ], heading="Person"),

        MultiFieldPanel([
            FieldPanel("twitter_title"),
            FieldPanel("twitter_username"),
        ], heading="Twitter feed"),
        MultiFieldPanel(
            [ImageChooserPanel("social_logo"), FieldPanel("social_url"), FieldPanel("social_link_text")],
            "Additional Social feed",
        ),
    ]



class MissionHome(HeroPage):
    template = "irelandie_assets/pages/mission.html"

    twitter_title = models.CharField(max_length=50, blank=True)
    root_navigation = StreamField(
        [("link", LinkBlock())], blank=True, help_text="Override the site navigation"
    )

    twitter_feed = models.ForeignKey(
        "utils.TwitterEmbed",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )

    root_page = models.BooleanField(null=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("root_page"),
        MultiFieldPanel([
            FieldPanel("twitter_title"),
            SnippetChooserPanel("twitter_feed"),
        ], heading="Twitter feed"),
    ]
    settings_panels = BasePage.settings_panels + [
        StreamFieldPanel("root_navigation")
    ]



class Magazine(HeroPage):
    template = "irelandie_assets/pages/magazine.html"
    
    body = StreamField(
            [
                ("rich_text", blocks.AdvancedRichTextBlock()),
                ("link_card", blocks.LinkCardsBlock())
            ],
            blank=True,
        )

    content_panels = HeroPage.content_panels + [
        StreamFieldPanel("body")
    ]
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel, heading='Hero'),
        ObjectList(HeroPage.promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])



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
                CountryPage.objects.descendant_of(self.get_parent())
                .filter(region=group)
                .count()
            )
            if countries_count:
                regions.append(group)

        return regions

    @cached_property
    def countries(self):
        return CountryPage.objects.descendant_of(self.get_parent())

    def get_context(self, request):
        context = super().get_context(request)
        context["regions"] = self.regions
        context["countries"] = self.countries
        return context


class ConsulatePage(FreeFormPageBase):
    template = "patterns/pages/missions/consulate_page.html"

    body = StreamField(blocks.FreeFormBlocksBase(), blank=True)

    parent_page_types = [
        "irelandie_missions.CountryPage",
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
            SnippetChooserPanel("twitter_feed"),
        ], heading="Twitter feed"),
    ]

    secondary_cta_panel = [
        StreamFieldPanel("secondary_call_to_action")
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
        "irelandie_missions.CountryPage",
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
            SnippetChooserPanel("twitter_feed"),
        ], heading="Twitter feed"),
    ]

    secondary_cta_panel = [
        StreamFieldPanel("secondary_call_to_action")
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

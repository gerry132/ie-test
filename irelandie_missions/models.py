from django.db import models
from django.utils.functional import cached_property
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from irelandie_home.models import HomePage
from irelandie_navigation.models import LinkBlock
from irelandie_utils import blocks
from irelandie_utils.models import BasePage, CountryGroup, HeroPage


class CountryGroupPageIndex(BasePage):
    template = "irelandie_assets/pages/countries.html"

    description = models.TextField(blank=True)
    override_primary_navigation = StreamField(
        [("link", LinkBlock())], blank=True, help_text="Override the site navigation"
    )

    parent_page_types = [HomePage]
    subpage_types = ["CountryPage"]

    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
    ]
    settings_panels = BasePage.settings_panels + [
        StreamFieldPanel("override_primary_navigation")
    ]


class CountryPage(HeroPage):
    template = "patterns/pages/missions/country_page.html"

    # parent_page_types = ["CountryGroupPageIndex"]
    subpage_types = ["MissionPage"]
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

    content_panels = HeroPage.content_panels + [
        SnippetChooserPanel("region"),
        StreamFieldPanel("stories"),
        StreamFieldPanel("embeds"),
        StreamFieldPanel("featured_stories"),
        StreamFieldPanel("featured_embassies"),
    ]


class MissionPage(BasePage):
    template = "irelandie_assets/pages/mission.html"

    parent_page_types = ["CountryPage"]
    subpage_types = [
        "irelandie_alerts.AlertPageIndex",
        "irelandie_contact_details.ContactDetailPageIndex",
        "irelandie_corporate_information.CorportateInformationPageIndex",
        "irelandie_news.NewsPageIndex",
        "irelandie_people.PersonPageIndex",
        "irelandie_people.RolePageIndex",
        "irelandie_places.PlacePageIndex",
        "irelandie_publications.PublicationPageIndex",
        "irelandie_site_information.SiteInformationPageIndex",
        "irelandie_speeches.SpeechPageIndex",
    ]


class MissionSearchPage(BasePage):
    template = "patterns/pages/missions/mission_search_page.html"

    description = models.TextField(blank=True)

    parent_page_types = [HomePage]
    subpage_types = []

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
        return CountryPage.objects.descendant_of(
            self.get_parent()
        )

    def get_context(self, request):
        context = super().get_context(request)
        context["regions"] = self.regions
        context["countries"] = self.countries
        return context

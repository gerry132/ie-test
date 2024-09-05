# -*- coding: utf-8 -*-
from django.db import models
from irelandie_utils.models import HeroPage, SocialFields, ListingFields
from irelandie_utils.blocks import GenericHeroBlock, ParallexAdvancedRichTextBlock, ParallaxImageVideoBlock, \
    ParallaxLogoCardsBlock, ParallaxStoryPhotoGalleryBlock, ParallaxTimelinePhotoGalleryBlock, ParallaxLinkCardsBlock, \
    ParallaxYoutubeVimeoBlock
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, MultiFieldPanel


class Parallax(HeroPage):
    template = "patterns/pages/irelandie_story/parallax_page.html"
    subtitle = models.TextField(blank=True)
    generic_hero = StreamField(
        [
            ("generic_hero", GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )

    body = StreamField(
        [
            ("ParallaxAdvancedRichTextBlock", ParallexAdvancedRichTextBlock()),
            ("ParallaxImageVideoBlock", ParallaxImageVideoBlock()),
            ("ParallaxYoutubeVimeoBlock", ParallaxYoutubeVimeoBlock()),
            ("ParallaxLogocards", ParallaxLogoCardsBlock()),
            ("ParallaxStoryPhotoGalleryBlock", ParallaxStoryPhotoGalleryBlock()),
            ("ParallaxTimelinePhotoGalleryBlock", ParallaxTimelinePhotoGalleryBlock()),
            ("ParallaxLinkCardsBlock", ParallaxLinkCardsBlock()),

        ],
        blank=True,
        null=True,
    )

    content_panels = HeroPage.content_panels + [
        FieldPanel("subtitle", help_text="Please include a brief description of this page/article. This will not "
                                         "appear live on the page, but will appear publicly as a subtitle in other "
                                         "areas of the site that link to this page."),
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("body"),
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

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HeroPage.hero_panel_with_size, heading='Hero'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(HeroPage.settings_panels, heading='Settings', classname="settings"),
    ])

    class Meta:
        verbose_name = "Parallax page"

# -*- coding: utf-8 -*-
from functools import cached_property

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.fields import StreamField
# from wagtailseo.models import SeoType

from irelandie_utils import blocks
from irelandie_utils.cache_invalidation import invalidate_page_cache
from irelandie_utils.utils import get_model_info

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import datetime
from wagtail.admin.forms import WagtailAdminPageForm

from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField

from irelandie_utils.models import MinimalArticlePage, BasePage

from django.dispatch import receiver
from django.db.models.signals import pre_delete

from wagtail.signals import page_published, page_unpublished
from wagtail.contrib.frontend_cache.utils import PurgeBatch


class NewsPageIndex(BasePage):
    template = "patterns/pages/irelandie_news/news_index.html"
    ajax_template = "patterns/molecules/article_card/ajax_article_card.html"
    description = models.TextField(blank=True)
    subpage_types = [
        'NewsPage'
    ]

    parent_page_types = [
        'NewsLandingPage'
    ]
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    # Indicate this is article-style content.
    # seo_content_type = SeoType.ARTICLE

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        year = None
        if request.GET.get('year'):
            if request.GET.get('year') == 'all':
                year = None
            else:
                year = int(request.GET.get('year'))
                low_date = datetime.datetime(year, 1, 1)
                high_date = datetime.datetime(year, 12, 31)

        elif 'year' in request.GET:
            if request.GET['year']:
                year = int(request.GET['year'])
                low_date = datetime.datetime(year, 1, 1)
                high_date = datetime.datetime(year, 12, 31)
            else:
                year = None
        else:
            high_date = datetime.datetime.now()
            low_date = datetime.datetime(high_date.year, 1, 1)
        if year:
            rel_art = (
                NewsPage.objects.child_of(self)
                .filter(publication_date__lte=high_date,
                        publication_date__gte=low_date,
                        locale=self.locale)
                .exclude(pk=self.pk)
                .public()
                .live()
                .order_by("-publication_date")
                .specific()
            )
        else:
            rel_art = (
                NewsPage.objects.child_of(self)
                .exclude(pk=self.pk)
                .public()
                .live()
                .order_by("-publication_date")
                .specific()
            )
        paginator = Paginator(rel_art, 10)
        # Try to get the ?page=x value
        page = request.GET.get("page", 1)
        try:
            rel_art = paginator.page(page)
        except PageNotAnInteger:
            rel_art = paginator.page(1)
        except EmptyPage:
            rel_art = paginator.page(paginator.num_pages)
        context['related_articles'] = rel_art
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name == 'mission page':
                missions = get_model_info(p.content_type.name, p.id)
                if missions.root_page:
                    context['mission_web_bot'] = missions.web_bot_script
        return context

    def get_news_items(self):
        # This returns a Django paginator of blog items in this section
        return Paginator(self.get_children().live().type(NewsPage), 20)

    @cached_property
    def get_years(self):
        yearset = (NewsPage.objects.child_of(self)
                   .public()
                   .live()
                   .order_by('-publication_date')
                   .values('publication_date')
                   .distinct()
                   )
        year_list = []
        for year in yearset:
            if year['publication_date'].year not in year_list:
                year_list.append(year['publication_date'].year)
        return year_list


class CustomNewsPageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].help_text = ("The page title as you'd like it to be seen by the public. Please ensure "
                                          "the page title entered here is unique. You should not"
                                          "create multiple news items with the same title, for example, "
                                          "'Newsletter'. If you post similar content on a monthly or quarterly "
                                          "basis, please ensure each one is uniquely named - for example, "
                                          "'September 2023 Embassy newsletter'.")


class NewsPage(MinimalArticlePage):
    template = "patterns/pages/irelandie_news/news_page.html"
    api_fields = [
        APIField('publication_date'),
        APIField('last_published_at'),
        APIField('hero_image'),
        APIField('year'),
        APIField('subtitle'),
        APIField('introduction'),
        APIField('hero_image_thumbnail', serializer=ImageRenditionField('fill-100x100', source='hero_image')),
    ]
    parent_page_types = [
        'NewsPageIndex'
    ]

    subpage_types = []

    @cached_property
    def related_articles(self):
        return (
            NewsPage.objects.exact_type(type(self))
            .child_of(self.get_parent())
            .filter(locale=self.locale, related_articles_active=True)
            .exclude(pk=self.pk)
            .public()
            .live()
            .order_by("-publication_date")[:4]
            .specific()
        )

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
            if p.content_type.name in ['mission page', 'Free Form Page']:
                missions = get_model_info(p.content_type.name, p.id)
                if missions.root_page:
                    context['default_image'] = missions.default_image
                if missions.root_page and missions.content_type.name == 'mission page':
                    context['mission_web_bot'] = missions.web_bot_script
        return context

    base_form_class = CustomNewsPageForm

    class Meta:
        verbose_name = "News Content"


def news_page_changed(news_page):
    news_index_page = Page.objects.live().type(NewsPageIndex).ancestor_of(news_page).specific().first()

    if news_index_page:
        news_landing_page = Page.objects.live().type(NewsLandingPage).ancestor_of(news_index_page).specific().first()

        if news_landing_page:
            # Find and purge paginated URLs
            paginator = news_index_page.get_news_items()
            total_pages = paginator.num_pages

            paginated_urls = []
            for i in range(1, total_pages + 1):
                paginated_url = f"{news_index_page.full_url}?page={i}"
                paginated_urls.append(paginated_url)

            batch = PurgeBatch()

            batch.add_page(news_landing_page)

            batch.add_page(news_index_page)

            for url in paginated_urls:
                batch.add_url(url)

            # Purge all added pages
            batch.purge()

            paginated_urls.append(news_index_page.url)
            paginated_urls.append(news_landing_page.url)
            # Handle cache invalidation for paginated URLs
            for url in paginated_urls:
                invalidate_page_cache(Page(url=url))


@receiver(page_published, sender=NewsPage)
def news_published_handler(instance, **kwargs):
    news_page_changed(instance)


@receiver(page_unpublished, sender=NewsPage)
def news_unpublished_handler(instance, **kwargs):
    news_page_changed(instance)


@receiver(pre_delete, sender=NewsPage)
def news_deleted_handler(instance, **kwargs):
    news_page_changed(instance)


class NewsLandingPage(BasePage):
    template = "patterns/pages/irelandie_news/news_landing_page.html"
    subpage_types = [
        'NewsPageIndex', 'irelandie_missions.GeneralContentPage',
    ]
    generic_hero = StreamField(
        [
            ("generic_hero", blocks.GenericHeroBlock()),
        ],
        blank=True,
        null=True,
        min_num=0,
        max_num=1,
    )
    link_button = StreamField(
        [
            ("link_button", blocks.LinkButtonBlock()),
        ],
        blank=True,
        null=True,
    )
    # Indicate this is article-style content.
    # seo_content_type = SeoType.ARTICLE

    content_panels = BasePage.content_panels + [
        FieldPanel("generic_hero", permission="access_admin", heading="Mini Hero Block"),
        FieldPanel("link_button")
    ]

    @cached_property
    def related_articles(self):
        if self.get_first_child():
            return (
                NewsPage.objects.child_of(self.get_first_child())
                .filter(locale=self.locale,
                        related_articles_active=True)
                .public()
                .live()
                .order_by("-publication_date")[:8]
                .specific()
            )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['get_news_index'] = (
            NewsPageIndex.objects.child_of(self)
            .public()
            .live()
            .specific()
        )
        pages = self.get_ancestors()
        for p in pages:
            if p.content_type.name in ['mission page', 'Free Form Page']:
                missions = get_model_info(p.content_type.name, p.id)
                if missions.root_page:
                    context['default_image'] = missions.default_image
                if missions.root_page and missions.content_type.name == 'mission page':
                    context['mission_web_bot'] = missions.web_bot_script

        return context

    @cached_property
    def get_years(self):
        if self.get_first_child():
            yearset = (NewsPage.objects.child_of(self.get_first_child())
                       .public()
                       .live()
                       .order_by()
                       .values('publication_date')
                       .distinct()
                       )
        year_list = []
        for year in yearset:
            if year['publication_date'].year not in year_list:
                year_list.append(year['publication_date'].year)
        return year_list

    @cached_property
    def get_root_index(self):
        if self.get_first_child():
            return self.get_first_child().url

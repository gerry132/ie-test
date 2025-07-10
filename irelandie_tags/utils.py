from itertools import chain
from operator import attrgetter
from django.db.models import F

from irelandie_news.models import NewsPage
from irelandie_parallax.models import Parallax


def get_tagged_items(self, tag):
    """
    Get tagged items, chain and return results.
    """
    from irelandie_pages.models import FreeFormPage
    from irelandie_story.models import StoryPage
    from irelandie_missions.models import GeneralContentPage

    freeform = FreeFormPage.objects.live().filter(
        page_related_tags__page=tag, locale=self.locale).specific().distinct().annotate(
        published=F('last_published_at'))
    stories = StoryPage.objects.live().filter(
        page_related_tags__page=tag, locale=self.locale).specific().distinct().annotate(
        published=F('last_published_at'))
    general_content = GeneralContentPage.objects.live().filter(
        page_related_tags__page=tag, locale=self.locale).specific().distinct().annotate(
        published=F('last_published_at'))
    news_content = NewsPage.objects.live().filter(
        page_related_tags__page=tag, locale=self.locale).specific().distinct().annotate(
        published=F('last_published_at'))
    parallax_content = Parallax.objects.live().filter(
        page_related_tags__page=tag, locale=self.locale).specific().distinct().annotate(
        published=F('last_published_at'))

    results = sorted(
        chain(stories, freeform, general_content, news_content, parallax_content),
        key=attrgetter('published'),
        reverse=True
    )

    return results

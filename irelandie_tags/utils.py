from itertools import chain
from operator import attrgetter

from django.db.models import Q


def get_tagged_items(self, tag):
    """
    Get tagged items, chain and return results.
    """
    from irelandie_pages.models import FreeFormPage
    from irelandie_story.models import StoryPage
    from irelandie_missions.models import GeneralContentPage

    dest = None
    if len(tag.related_destinations) != 0:
        dest = tag.related_destinations[0]

    freeform = FreeFormPage.objects.live().filter(
        Q(page_related_tags__page=tag) | Q(page_related_destinations__page=dest),
        locale=self.locale).specific().distinct()
    stories = StoryPage.objects.live().filter(
        Q(page_related_tags__page=tag) | Q(page_related_destinations__page=dest),
        locale=self.locale).specific().distinct()
    general_content = GeneralContentPage.objects.live().filter(
        Q(page_related_tags__page=tag) | Q(page_related_destinations__page=dest),
        locale=self.locale).specific().distinct()

    results = sorted(
        chain(stories, freeform, general_content),
        key=attrgetter('last_published_at')
    )

    return results

from itertools import chain
from operator import attrgetter


def get_tagged_items(self, tag):
    """
    Get tagged items, chain and return results.
    """
    from irelandie_pages.models import FreeFormPage
    from irelandie_story.models import StoryPage
    from irelandie_missions.models import GeneralContentPage

    freeform = FreeFormPage.objects.live().filter(
        page_related_tags__page=tag, locale=self.locale).specific().distinct()
    stories = StoryPage.objects.live().filter(
        page_related_tags__page=tag, locale=self.locale).specific().distinct()
    general_content = GeneralContentPage.objects.live().filter(
        page_related_tags__page=tag, locale=self.locale).specific().distinct()

    results = sorted(
        chain(stories, freeform, general_content),
        key=attrgetter('last_published_at')
    )

    return results

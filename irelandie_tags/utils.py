from itertools import chain
from operator import attrgetter


def get_tagged_items(self, tag):
    """
    Get tagged items, chain and return results.
    """
    from irelandie_pages.models import FreeFormPage
    from irelandie_story.models import StoryPage
    from irelandie_missions.models import GeneralContentPage

    freeform = FreeFormPage.objects.live().filter(locale=self.locale, page_related_tags__page=tag).specific()
    stories = StoryPage.objects.live().filter(locale=self.locale, page_related_tags__page=tag).specific()
    general_content = GeneralContentPage.objects.live().filter(
        locale=self.locale, page_related_tags__page=tag).specific()

    results = sorted(
        chain(stories, freeform, general_content),
        key=attrgetter('last_published_at')
    )
    return results

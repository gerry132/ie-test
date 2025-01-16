from django.dispatch import receiver
from wagtail.contrib.frontend_cache.utils import PurgeBatch
from django.dispatch import Signal
from wagtail.core.signals import page_published

from irelandie_utils.cache_invalidation import invalidate_snippet_cache

snippet_published = Signal()


@receiver(snippet_published)
def handle_snippet_published(sender, instance, **kwargs):
    usage = instance.get_usage()

    purge_batch = PurgeBatch()
    for page, _ in usage:
        purge_batch.add_url(page.url)
    purge_batch.purge()

    invalidate_snippet_cache(instance)


@receiver(page_published)
def handle_page_published(sender, instance, **kwargs):
    from irelandie_tags.models import MegaTagLanding, MegaTagIndexPage, TagLandingPage, TagIndexPage
    # Get all related tags
    tags = instance.page_related_tags.all()

    # Find all landing and index pages associated with these tags
    pages_to_purge = []

    for tag_relation in tags:
        tag = tag_relation.page
        megataglanding = MegaTagLanding.objects.live().filter(
            page_related_tags__page=tag, locale=instance.locale).specific().distinct()
        taglanding = TagLandingPage.objects.live().filter(
            page_related_tags__page=tag, locale=instance.locale).specific().distinct()
        for landing_page in megataglanding:
            child_index_pages = landing_page.get_children().type(MegaTagIndexPage).specific().distinct()
            pages_to_purge.extend(child_index_pages)

        for landing_page in taglanding:
            child_index_pages = landing_page.get_children().type(TagIndexPage).specific().distinct()
            pages_to_purge.extend(child_index_pages)
        pages_to_purge.extend(megataglanding)
        pages_to_purge.extend(taglanding)

    purge_batch = PurgeBatch()
    for page in set(pages_to_purge):
        purge_batch.add_url(page.full_url)

    # Purge the collected URLs
    purge_batch.purge()

from django.dispatch import receiver
from wagtail.contrib.frontend_cache.utils import PurgeBatch
from django.dispatch import Signal

snippet_published = Signal()

@receiver(snippet_published)
def handle_snippet_published(sender, instance, **kwargs):
    usage = instance.get_usage()

    purge_batch = PurgeBatch()
    for page, _ in usage:
        purge_batch.add_url(page.url)
    purge_batch.purge()

import boto3
import time
from django.core.cache import cache
from django.conf import settings


def invalidate_cloudfront(paths):

    if settings.DJANGO_ENV != 'local':
        distribution_id = settings.WAGTAILFRONTENDCACHE['cloudfront']['DISTRIBUTION_ID']

        client = boto3.client('cloudfront')
        response = client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths,
                },
                'CallerReference': str(time.time()).replace('.', '')
            }
        )
        return response
    else:
        print("CloudFront invalidation is not configured.")
        return None


def invalidate_page_cache(page):
    paths_to_invalidate = [page.url]
    print(paths_to_invalidate)

    if paths_to_invalidate:
        invalidate_cloudfront(paths_to_invalidate)

    from irelandie_missions.models import EmbassyIndexPage
    if isinstance(page, EmbassyIndexPage):
        cache_key = f'embassy_index:{page.url}'
        cache.delete(cache_key)


def invalidate_snippet_cache(snippet_instance):
    usage = snippet_instance.get_usage()

    paths_to_invalidate = [page.url for page, _ in usage]

    if paths_to_invalidate:
        invalidate_cloudfront(paths_to_invalidate)

    for page in usage:
        from irelandie_missions.models import EmbassyIndexPage
        if isinstance(page, EmbassyIndexPage):
            cache_key = f'embassy_index:{page.url}'
            cache.delete(cache_key)

import boto3
import time
from django.core.cache import cache
from django.conf import settings
from django.core.cache.utils import make_template_fragment_key

from irelandie_assets.templatetags.irelandie_assets_tags import check_page_type


def invalidate_cloudfront(paths):
    distribution_id = getattr(settings, "CLOUDFRONT_ID", None)

    if distribution_id:
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
        print("No CloudFront Distribution ID provided.")
        return


def invalidate_page_cache(page):
    paths_to_invalidate = [page.url]

    if paths_to_invalidate:
        invalidate_cloudfront(paths_to_invalidate)

    if check_page_type(page.content_type, 'embassy index page'):
        key = make_template_fragment_key("embassy_index")
        cache.delete(key)


def invalidate_snippet_cache(snippet_instance):
    usage = snippet_instance.get_usage()

    paths_to_invalidate = [page.url for page, _ in usage]

    if paths_to_invalidate:
        invalidate_cloudfront(paths_to_invalidate)

    for page_tuple in usage:
        page_type = page_tuple[0]
        if check_page_type(page_type.content_type, 'embassy index page'):
            key = make_template_fragment_key("embassy_index")
            cache.delete(key)

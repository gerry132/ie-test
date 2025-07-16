import boto3
import time

from botocore.exceptions import ClientError
from django.core.cache import cache
from django.conf import settings
from django.core.cache.utils import make_template_fragment_key
from wagtail.models import Page

from irelandie_assets.templatetags.irelandie_assets_tags import check_page_type


def invalidate_cloudfront(paths):
    distribution_id = getattr(settings, "CLOUDFRONT_ID", None)

    if distribution_id:
        client = boto3.client('cloudfront')

        try:
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

        except client.exceptions.NoSuchDistribution as e:
            # Log or handle the NoSuchDistribution error silently
            print(f"CloudFront distribution {distribution_id} does not exist. Error: {e}")
            return None

        except ClientError as e:
            # Handle other ClientError exceptions (optional)
            print(f"An error occurred: {e}")
            return None
    else:
        print("No CloudFront Distribution ID provided.")
        return None


def invalidate_page_cache(paths_to_invalidate):

    if paths_to_invalidate:
        invalidate_cloudfront(paths_to_invalidate)


def invalidate_cache(snippet_instance):
    usage = snippet_instance.get_usage()
    paths_to_invalidate = []

    for obj, _ in usage:
        if isinstance(obj, Page):
            if obj.url:
                paths_to_invalidate.append(obj.url)

    if paths_to_invalidate:
        invalidate_cloudfront(paths_to_invalidate)

    for obj, _ in usage:
        if isinstance(obj, Page):
            if check_page_type(obj.content_type, 'embassy index page'):
                key = make_template_fragment_key("embassy_index")
                cache.delete(key)

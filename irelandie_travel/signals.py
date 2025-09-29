from django.dispatch import receiver
from wagtail.signals import page_published
from .models import TravelCountryPage


@receiver(page_published, sender=TravelCountryPage)
def update_translation_status(instance, **kwargs):
    """
    Add signal to update travel restrictions.
    """

    for i in instance.get_translations():
        i.travel_caution_level = instance.travel_caution_level
        i.save()

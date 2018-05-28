from django.db.models.signals import post_save
from django.dispatch import receiver

from google_address import helpers
from google_address.models import Address
from google_address.update import update_address, UpdateThread


@receiver(post_save, sender=Address)
def address_post_save(sender, instance, **kwargs):
    # If raw == True, we should not modify the record
    #
    # https://docs.djangoproject.com/en/1.11/ref/signals/#post-save
    if kwargs.get('raw', False):  # pragma: no cover
        return None

    if helpers.get_settings().get("ASYNC_CALLS", False):
        thread = UpdateThread(instance)
        thread.start()
        return thread
    else:
        return update_address(instance)

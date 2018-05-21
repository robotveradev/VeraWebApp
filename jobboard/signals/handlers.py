from django.db.models.signals import post_save
from django.dispatch import receiver

from jobboard.models import Candidate, Employer
from jobboard.tasks import new_role_instance


@receiver(post_save, sender=Employer)
@receiver(post_save, sender=Candidate)
def create_contract(sender, instance, created, **kwargs):
    if created:
        new_role_instance.delay(instance.id, instance.__class__.__name__)

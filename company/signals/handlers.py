from django.db.models.signals import post_save
from django.dispatch import receiver

from company.models import Company
from company.tasks import deploy_new_company


@receiver(post_save, sender=Company)
def company_created(sender, instance, created, **kwargs):
    if created:
        deploy_new_company.delay(instance.id)

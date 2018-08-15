from django.db.models.signals import post_save
from django.dispatch import receiver

from pipeline.models import Pipeline
from vacancy.models import Vacancy, MemberOnVacancy
from vacancy.tasks import new_vacancy, change_status, change_vacancy_allowed_amount, new_subscribe


@receiver(post_save, sender=Vacancy)
def handler_new_vacancy(sender, instance, created, **kwargs):
    if created:
        new_vacancy.delay(instance.id)
        Pipeline.objects.create(vacancy=instance)


@receiver(post_save, sender=MemberOnVacancy)
def new_subscribe_entry(sender, instance, created, **kwargs):
    if created:
        new_subscribe.delay(instance.member.id, instance.vacancy.id)


@receiver(post_save, sender=Vacancy)
def change_vacancy_status(sender, instance, created, **kwargs):
    if instance.published:
        if hasattr(instance, 'change_status') and instance.change_status:
            change_status.delay(instance.id, instance.changed_by.id)
        elif hasattr(instance, 'allowed_changed') and instance.allowed_changed:
            change_vacancy_allowed_amount.delay(instance.id, instance.changed_by.id)

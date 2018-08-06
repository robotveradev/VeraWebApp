from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from jobboard.handlers.candidate import CandidateHandler
from jobboard.tasks import save_txn_to_history, save_txn
from pipeline.models import Pipeline
from vacancy.models import Vacancy, MemberOnVacancy
from vacancy.tasks import new_vacancy, change_status, change_vacancy_allowed_amount


@receiver(post_save, sender=Vacancy)
def handler_new_vacancy(sender, instance, created, **kwargs):
    if created:
        new_vacancy.delay(instance.id)
        Pipeline.objects.create(vacancy=instance)


@receiver(post_save, sender=MemberOnVacancy)
def new_subscribe(sender, instance, created, **kwargs):
    if created:
        candidate_h = CandidateHandler(account=settings.WEB_ETH_COINBASE,
                                       contract_address=instance.candidate.contract_address)
        txn_hash = candidate_h.subscribe(instance.vacancy.uuid)
        if txn_hash:
            user_id = instance.candidate.user.id
            save_txn.delay(txn_hash.hex(), 'Subscribe', user_id, instance.vacancy.id)
            save_txn_to_history.delay(user_id, txn_hash.hex(), 'Subscribe to vacancy {}'.format(instance.vacancy.title))
        else:
            instance.delete()


@receiver(post_save, sender=Vacancy)
def change_vacancy_status(sender, instance, created, **kwargs):
    if instance.published:
        if hasattr(instance, 'change_status') and instance.change_status:
            change_status.delay(instance.id, instance.change_by.id)
        elif hasattr(instance, 'allowed_changed') and instance.allowed_changed:
            change_vacancy_allowed_amount.delay(instance.id)

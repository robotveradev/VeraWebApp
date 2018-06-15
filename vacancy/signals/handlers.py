from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from jobboard.handlers.new_candidate import CandidateHandler
from pipeline.models import Pipeline
from vacancy.models import Vacancy, ProfileOnVacancy
from jobboard.tasks import save_txn_to_history, save_txn
from vacancy.tasks import new_vacancy


@receiver(post_save, sender=Vacancy)
def handler_new_vacancy(sender, instance, created, **kwargs):
    if created:
        new_vacancy.delay(instance.id)
        Pipeline.objects.create(vacancy=instance)


@receiver(post_save, sender=ProfileOnVacancy)
def new_subscribe(sender, instance, created, **kwargs):
    #TODO change
    if created:
        candidate_h = CandidateHandler(settings.WEB_ETH_COINBASE, instance.cv.candidate.contract_address)
        txn_hash = candidate_h.subscribe(instance.vacancy.uuid, instance.cv.uuid)
        if txn_hash:
            user_id = instance.cv.candidate.user.id
            save_txn.delay(txn_hash.hex(), 'Subscribe', user_id, instance.vacancy.id)
            save_txn_to_history.delay(user_id, txn_hash.hex(), 'Subscribe to vacancy {}'.format(instance.vacancy.title))
        else:
            instance.delete()

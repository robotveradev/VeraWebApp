from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from jobboard.handlers.new_candidate import CandidateHandler
from jobboard.handlers.new_oracle import OracleHandler
from vacancy.models import Vacancy, CVOnVacancy
from jobboard.tasks import save_txn_to_history, save_txn


@receiver(post_save, sender=Vacancy)
def change_vacancy_paused(sender, instance, created, **kwargs):
    if instance.enabled is None and instance.published:
        oracle = OracleHandler()
        if oracle.get_vacancy_paused(instance.uuid):
            txn_hash = oracle.unpause_vac(instance.uuid)
        else:
            txn_hash = oracle.pause_vac(instance.uuid)

        save_txn.delay(txn_hash, 'vacancyChange', instance.employer.user.id, instance.id)
        save_txn_to_history.delay(instance.employer.user.id, txn_hash,
                                  'Change vacancy {} status'.format(instance.uuid))


@receiver(post_save, sender=CVOnVacancy)
def new_subscribe(sender, instance, created, **kwargs):
    if created:
        candidate_h = CandidateHandler(settings.WEB_ETH_COINBASE, instance.cv.candidate.contract_address)
        txn_hash = candidate_h.subscribe(instance.vacancy.uuid, instance.cv.uuid)
        if txn_hash:
            user_id = instance.cv.candidate.user.id
            save_txn.delay(txn_hash, 'Subscribe', user_id, instance.vacancy.id)
            save_txn_to_history.delay(user_id, txn_hash, 'Subscribe to vacancy {}'.format(instance.vacancy.title))
        else:
            instance.delete()

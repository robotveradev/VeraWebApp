from django.db.models.signals import post_save
from django.dispatch import receiver
from jobboard.handlers.new_oracle import OracleHandler
from candidateprofile.models import CandidateProfile
from jobboard.tasks import save_txn_to_history, save_txn
from candidateprofile.tasks import new_cv


@receiver(post_save, sender=CandidateProfile)
def change_cv_paused(sender, instance, created, **kwargs):
    if created:
        new_cv.apply_async(args=(instance.id, ), countdown=2)
    elif instance.enabled is None and instance.published is True:
        oracle = OracleHandler()
        if oracle.get_cv_paused(instance.uuid) is True:
            txn_hash = oracle.unpause_cv(instance.uuid)
        else:
            txn_hash = oracle.pause_cv(instance.uuid)

        save_txn.delay(txn_hash, 'cvChange', instance.candidate.user.id, instance.id)
        save_txn_to_history.delay(instance.candidate.user.id, txn_hash,
                                  'Change profile {} status'.format(instance.uuid))

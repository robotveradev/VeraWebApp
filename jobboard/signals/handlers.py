from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from web3 import Web3
from jobboard.tasks import save_txn_to_history, save_txn
from jobboard.handlers.oracle import OracleHandler
from jobboard.models import Candidate, Employer


@receiver(post_save, sender=Candidate)
def create_candidate_contract(sender, instance, created, **kwargs):
    if created:
        oracle = OracleHandler()
        txn_hash = oracle.new_candidate(
            Web3.toBytes(hexstr=Web3.sha3(
                text=instance.first_name + instance.middle_name + instance.last_name + instance.tax_number)))
        if txn_hash:
            save_txn_to_history.delay(instance.user.id, txn_hash, 'Creation of a new candidate contract')
            save_txn.delay(txn_hash, 'NewCandidate', instance.user.id, instance.id)


@receiver(post_save, sender=Employer)
def create_employer_contract(sender, instance, created, **kwargs):
    if created:
        oracle = OracleHandler()
        txn_hash = oracle.new_employer(Web3.toBytes(hexstr=Web3.sha3(text=instance.organization + instance.tax_number)),
                                       settings.VERA_COIN_CONTRACT_ADDRESS)
        if txn_hash:
            save_txn_to_history.delay(instance.user.id, txn_hash, 'Creation of a new employer contract')
            save_txn.delay(txn_hash, 'NewEmployer', instance.user.id, instance.id)

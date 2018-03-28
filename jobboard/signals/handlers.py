from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from web3 import Web3

from jobboard.handlers.employer import EmployerHandler
from jobboard.tasks import save_txn_to_history, save_txn
from jobboard.handlers.oracle import OracleHandler
from jobboard.models import Candidate, Employer, Transaction


@receiver(post_save, sender=Employer)
@receiver(post_save, sender=Candidate)
def create_contract(sender, instance, created, **kwargs):
    if created:
        oracle = OracleHandler()
        method = getattr(oracle, 'new_' + instance.__class__.__name__.lower())
        txn_hash = method(instance.contract_id)
        if txn_hash:
            save_txn_to_history.delay(instance.user.id, txn_hash,
                                      'Creation of a new {} contract'.format(instance.__class__.__name__))
            save_txn.delay(txn_hash, 'New' + instance.__class__.__name__, instance.user.id, instance.id)
        else:
            instance.delete()


@receiver(post_save, sender=Employer)
@receiver(post_save, sender=Candidate)
def change_contract_status(sender, instance, created, **kwargs):
    if instance.contract_address and instance.enabled is None:
        status_changed = getattr(instance, '_status_changed', False)
        if status_changed:
            oracle = OracleHandler()
            obj_h = EmployerHandler(settings.WEB_ETH_COINBASE, instance.contract_address)
            if obj_h.paused():
                txn_hash = oracle.unpause_contract(instance.contract_address)
            else:
                txn_hash = oracle.pause_contract(instance.contract_address)

            if txn_hash:
                save_txn.delay(txn_hash, instance.__class__.__name__.lower() + 'Change', instance.user.id,
                               instance.id)
                save_txn_to_history.delay(instance.user.id, txn_hash,
                                          '{} change contract {} status'.format(
                                              instance.__class__.__name__.capitalize(),
                                              instance.contract_address))

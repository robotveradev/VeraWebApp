from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task
from solc import compile_files

from company.models import Company
from jobboard.handlers.oracle import OracleHandler
from jobboard import utils
from jobboard.tasks import create_abi, save_txn, save_txn_to_history
from vera import settings

logger = logging.getLogger(__name__)


@shared_task
def verify_company(company_id):
    """Must set company.verified = True if company verified successfully"""
    return True


@shared_task
def deploy_new_company(company_id):
    """
    Deploy new company contract
    :param company_id: Company off chain id for deploy
    :return: True in case of successful, false otherwise
    """
    try:
        instance = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        logger.error('Company with id {} not found, contract will bot be deployed.'.format(company_id))
    else:
        oracle = OracleHandler()
        w3 = utils.get_w3()
        contract_file = 'dapp/contracts/Company.sol'
        compile_sol = compile_files([contract_file, ],
                                    output_values=("abi", "ast", "bin", "bin-runtime",))
        create_abi(compile_sol[contract_file + ':Company']['abi'], 'Company')
        obj = w3.eth.contract(
            abi=compile_sol[contract_file + ':Company']['abi'],
            bytecode=compile_sol[contract_file + ':Company']['bin'],
            bytecode_runtime=compile_sol[contract_file + ':Company']['bin-runtime'],
        )
        args = [settings.VERA_COIN_CONTRACT_ADDRESS, settings.VERA_ORACLE_CONTRACT_ADDRESS, ]
        logger.info('Try to unlock account: {}.'.format(oracle.unlockAccount()))
        try:
            txn_hash = obj.deploy(transaction={'from': oracle.account}, args=args)
        except Exception as e:
            logger.warning('Error while deploy new company contract. Company {}, ex {}'.format(company_id, e))
        else:
            logger.info('Lock account: {}'.format(oracle.lockAccount()))
            save_txn.delay(txn_hash.hex(), 'NewCompany', company_id, instance.created_by.id)
            save_txn_to_history.delay(instance.created_by.id, txn_hash.hex(),
                                      'Creation of a new Company contract')

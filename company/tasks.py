from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task
from solc import compile_files

from company.models import Company
from jobboard import utils
from jobboard.handlers.member import MemberInterface
from jobboard.handlers.oracle import OracleHandler
from jobboard.tasks import create_abi, save_txn, save_txn_to_history
from users.models import Member
from users.utils import company_member_role
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
            save_txn.delay(txn_hash.hex(), 'NewCompany', instance.created_by.id, company_id)
            save_txn_to_history.delay(instance.created_by.id, txn_hash.hex(),
                                      'Creation of a new Company contract')


@shared_task
def set_member_role(company_address, sender_id, member_id, role):
    try:
        sender = Member.objects.get(pk=sender_id)
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        logger.warning('Member not found and will not be added to company.')
    else:
        mi = MemberInterface(sender.contract_address)
        try:
            if role == 'owner':
                txn_hash = mi.new_company_owner(company_address, member.contract_address)
            elif role == 'collaborator':
                txn_hash = mi.new_company_collaborator(company_address, member.contract_address)
            else:
                txn_hash = mi.new_company_member(company_address, member.contract_address)
        except Exception as e:
            logger.error(
                'Error while add member to company {} {} {} {}'.format(company_address, member_id, sender_id, e))
        else:
            save_txn.delay(txn_hash.hex(), 'AddCompanyMember', sender_id, member_id)
            save_txn_to_history.delay(sender_id, txn_hash.hex(), 'Add {} as company member'.format(member.full_name))
            return True


@shared_task
def change_member_role(company_address, member_id, sender_id, role):
    try:
        sender = Member.objects.get(pk=sender_id)
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        logger.warning('Member not found and will not be added to company.')
    else:
        mi = MemberInterface(sender.contract_address)
        c_role = company_member_role(company_address, member.contract_address)
        if role == c_role:
            return False

        if c_role == 'owner':
            try:
                mi.del_owner_member(company_address, member.contract_address)
            except Exception as e:
                logger.warning('Cant delete owner member role: {} {}'.format(member_id, e))
        elif c_role == 'collaborator':
            try:
                mi.del_collaborator_member(company_address, member.contract_address)
            except Exception as e:
                logger.warning('Cant delete collaborator member role: {} {}'.format(member_id, e))

        method = getattr(mi, 'new_company_{}'.format(role))
        try:
            txn_hash = method(company_address, member.contract_address)
        except Exception as e:
            logger.warning('Cant add {} member role: {} {}'.format(role, member_id, e))
        else:
            save_txn.delay(txn_hash.hex(), 'ChangeCompanyMember', sender_id, member_id)
            save_txn_to_history.delay(sender_id, txn_hash.hex(),
                                      'Change {} as company {}'.format(member.full_name, role))
            return True

from authy.api import AuthyApiClient
from django.conf import settings

from jobboard.handlers.company import CompanyInterface
from jobboard.handlers.oracle import OracleHandler

authy_api = AuthyApiClient(api_key=settings.AUTHY_API_KEY)


def send_verfication_code(phone_number, country_code, via):
    request = authy_api.phones.verification_start(phone_number, country_code, via)
    return request.content


def verify_sent_code(one_time_password, user):
    check = authy_api.phones.verification_check(user.phone_number, user.country_code, one_time_password)
    return check.content


def company_member_role(company_address, member_address):
    oracle = OracleHandler()
    member_companies = oracle.get_member_companies(member_address)
    if company_address in member_companies:
        ci = CompanyInterface(contract_address=company_address)
        is_owner = ci.is_owner(member_address)
        if is_owner:
            return 'owner'
        is_collaborator = ci.is_collaborator(member_address)
        if is_collaborator:
            return 'collaborator'
        return 'member'
    return None

from authy.api import AuthyApiClient
from django.conf import settings

authy_api = AuthyApiClient(api_key=settings.AUTHY_API_KEY)


def send_verfication_code(phone_number, country_code, via):
    request = authy_api.phones.verification_start(phone_number, country_code, via)
    return request.content


def verify_sent_code(one_time_password, user):
    check = authy_api.phones.verification_check(user.phone_number, user.country_code, one_time_password)
    return check.content

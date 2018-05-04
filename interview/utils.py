from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from .models import Interview
from django.db.models import Q
import logging
import sys


def get_user_from_session(session_key):
    """
    Gets the user from current User model using the passed session_key
    :param session_key: django.contrib.sessions.models.Session - session_key
    :return: User instance or None if not found
    """
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    uid = session_data.get('_auth_user_id')
    user = get_user_model().objects.filter(id=uid).first()  # get object or none
    return user


def get_interview_by_id(interview_id):
    return Interview.objects.filter(id=interview_id)


def get_dialogs_with_user(user_1, user_2):
    """
    gets the dialog between user_1 and user_2
    :param user_1: the first user in dialog (owner or opponent)
    :param user_2: the second user in dialog (owner or opponent)
    :return: queryset which include dialog between user_1 and user_2 (queryset can be empty)
    """
    return Interview.objects.filter(
        Q(action_interview__action__pipeline__vacancy__employer__user=user_1, cv__candidate__user=user_2) |
        Q(cv__candidate__user=user_1, action_interview__action__pipeline__vacancy__employer__user=user_2))


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    datefmt='%d.%m.%y %H:%M:%S')
logger = logging.getLogger('django-private-dialog')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

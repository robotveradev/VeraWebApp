from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import Candidate, Employer


def user_role(user):
    if isinstance(user, AnonymousUser):
        return None, None
    try:
        return 'employer', Employer.objects.get(user=user)
    except Employer.DoesNotExist:
        try:
            return 'candidate', Candidate.objects.get(user=user)
        except Candidate.DoesNotExist:
            return None, None


class RoleMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'user'), (
         "The Jobboard role middleware requires authentication middleware "
         "to be installed. Edit your MIDDLEWARE%s setting to insert "
         "'django.contrib.auth.middleware.AuthenticationMiddleware' before "
         "'jobboard.middleware.RoleMiddleware'"
         ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        user = request.user

        request.role, request.role_object = user_role(user)

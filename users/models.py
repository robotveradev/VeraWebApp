import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models

from jobboard.handlers.oracle import OracleHandler
from users.manager import MemberManager


class Member(AbstractUser):
    name = models.CharField(blank=True, max_length=255)
    phone_number_verified = models.BooleanField(default=False)
    change_pw = models.BooleanField(default=True)
    phone_number = models.BigIntegerField(unique=True)
    country_code = models.CharField(max_length=15)
    two_factor_auth = models.BooleanField(default=False)
    contract_address = models.CharField(max_length=42,
                                        blank=True,
                                        null=True)
    tax_number = models.CharField(max_length=255,
                                  blank=False,
                                  null=False)

    objects = MemberManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number', 'country_code', 'tax_number']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def companies(self):
        _model = ContentType.objects.get(model='company')
        if not self.contract_address:
            return _model.model_class().objects.none()
        oracle = OracleHandler()
        companies = oracle.get_member_companies(self.contract_address)
        return _model.model_class().objects.filter(contract_address__in=companies)

    def get_short_name(self):
        """
        Returns the display name.
        If full name is present then return full name as display name
        else return username.
        """
        if self.name != '':
            return self.name
        else:
            return self.username


class InviteCode(models.Model):
    code = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    expired = models.BooleanField(default=False)
    one_off = models.BooleanField(default=True)
    session_key = models.CharField(max_length=64,
                                   blank=True,
                                   null=True,
                                   default=None)
    used_by = models.ForeignKey(Member,
                                blank=True,
                                null=True,
                                default=None,
                                on_delete=models.SET_NULL)

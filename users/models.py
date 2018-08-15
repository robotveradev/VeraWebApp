import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

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

    objects = MemberManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number', 'country_code']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def job_status(self):
        return OracleHandler().member_status(self.contract_address, only_index=True)

    @property
    def companies(self):
        """
        Filter for companies member is in.
        :return: Companies QuerySet
        """
        _model = ContentType.objects.get(model='company')
        if not self.contract_address:
            return _model.model_class().objects.none()
        companies = OracleHandler().get_member_companies(self.contract_address)
        return _model.model_class().objects.filter(contract_address__in=companies)

    @property
    def vacancies(self):
        """
        Filter for vacancies member subscribed to
        :return: Vacancies QuerySet
        """
        _model = ContentType.objects.get(model='vacancy')
        if not self.contract_address:
            return _model.model_class().objects.none()
        vac_set = set()
        oracle = OracleHandler()
        vac_length = oracle.member_vacancies_length(self.contract_address)
        for i in range(vac_length):
            vac_uuid = oracle.member_vacancy_by_index(self.contract_address, i)
            vac_set.add(vac_uuid)
        vacancies = _model.model_class().objects.filter(uuid__in=vac_set)
        return vacancies

    def current_action_index(self, vacancy):
        """
        Get member current action number for given vacancy
        :param vacancy: vacancy to find action number
        :return: int (action number) or -1 (not subscribed to vacancy)
        """
        return OracleHandler().get_member_current_action_index(vacancy.company.contract_address, vacancy.uuid,
                                                               self.contract_address)

    @property
    def verified(self):
        """
        Is member verified in system
        :return: bool
        """
        return OracleHandler().member_verified(self.contract_address)

    def verify(self):
        """
        Verify user
        :return: txn_hash in hex object
        """
        return OracleHandler().verify_member(self.contract_address)

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

    def is_already_verify_fact(self, member_address, fact_id):
        """
        Returns true if current user already verify member fact
        :param member_address: Member fact verified for
        :param fact_id: fact id
        :return: bool
        """
        return OracleHandler().member_fact_confirmations(self.contract_address, member_address, fact_id)

    def get_absolute_url(self):
        return reverse('member_profile', kwargs={'username': self.username})


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

from django.contrib.auth.models import User
from django.db import models


class Keyword(models.Model):
    word = models.CharField(max_length=32)

    def __str__(self):
        return self.word


class Specialisation(models.Model):
    parent_specialisation = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def parent(self):
        if self.parent_specialisation is not None:
            return str(self.parent_specialisation)


class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contract_address = models.CharField(max_length=64, null=True, blank=True)
    first_name = models.CharField(max_length=64, null=False, blank=False)
    middle_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=False, blank=False)
    tax_number = models.CharField(max_length=32, blank=False, null=False)
    enabled = models.NullBooleanField(default=None)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + self.tax_number + ')'

    def disable(self):
        self.enabled = False
        self.save()

    def enable(self):
        assert (self.contract_address is not None), (
            "%s contract address must be not None for enable"
            ) % self.__class__.__name__
        self.enabled = True
        self.save()

    @property
    def full_name(self):
        return '%s %s%s' % (self.first_name, self.last_name, ' ' + self.middle_name if self.middle_name else '')


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contract_address = models.CharField(max_length=64, null=True, blank=True)
    organization = models.CharField(max_length=255, null=False, blank=False)
    tax_number = models.CharField(max_length=32, null=False, blank=False)
    enabled = models.NullBooleanField(default=None)

    def __str__(self):
        return self.organization + ' (' + self.tax_number + ')'

    def disable(self):
        self.enabled = False
        self.save()

    def enable(self):
        assert (self.contract_address is not None), (
            "%s contract address must be not None for enable"
            ) % self.__class__.__name__
        self.enabled = True
        self.save()


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    txn_hash = models.CharField(max_length=127)
    txn_type = models.CharField(max_length=31)
    obj_id = models.SmallIntegerField(default=0)
    vac_id = models.SmallIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + self.txn_hash


class TransactionHistory(models.Model):
    hash = models.CharField(max_length=127)
    action = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {}'.format(self.user.username, self.hash)

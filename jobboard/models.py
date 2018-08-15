from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from web3 import Web3

from vacancy.models import Vacancy

User = get_user_model()


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


class Transaction(models.Model):
    user = models.SmallIntegerField(default=0)
    txn_hash = models.CharField(max_length=127)
    txn_type = models.CharField(max_length=31)
    obj_id = models.CharField(max_length=127)
    vac_id = models.SmallIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.txn_hash


class TransactionHistory(models.Model):
    hash = models.CharField(max_length=127)
    action = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.hash

    class Meta:
        ordering = ('-created_at',)

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.manager import CustomUserManager


class CustomUser(AbstractUser):
    # First/last name is not a global-friendly pattern
    name = models.CharField(blank=True, max_length=255)
    phone_number_verified = models.BooleanField(default=False)
    change_pw = models.BooleanField(default=True)
    phone_number = models.BigIntegerField(unique=True)
    country_code = models.CharField(max_length=15)
    two_factor_auth = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number', 'country_code']

    def __str__(self):
        return self.username

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
    used_by = models.ForeignKey(CustomUser,
                                blank=True,
                                null=True,
                                default=None,
                                on_delete=models.SET_NULL)

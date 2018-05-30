from django.db import models

from google_address.models import Address
from jobboard.models import Employer


class Company(models.Model):
    employer = models.ForeignKey(Employer,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='companies')
    logo = models.ImageField(null=True)
    name = models.CharField(max_length=512,
                            null=False,
                            blank=False)
    tax_number = models.CharField(max_length=64,
                                  null=False,
                                  blank=False)
    legal_address = models.ForeignKey(Address,
                                      on_delete=models.SET_NULL,
                                      null=True)
    work_sector = models.CharField(max_length=512)
    date_created = models.DateField(null=True,
                                    blank=True)
    site = models.URLField(null=True,
                           blank=True)
    description = models.TextField(blank=False,
                                   null=False)
    phone = models.CharField(max_length=31)
    email = models.EmailField()
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Office(models.Model):
    company = models.ForeignKey(Company,
                                on_delete=models.CASCADE,
                                related_name='offices')
    address = models.ForeignKey(Address,
                                on_delete=models.SET_NULL,
                                null=True)
    main = models.BooleanField(default=False)

    def __str__(self):
        return self.address.address_line


class SocialLink(models.Model):
    company = models.ForeignKey(Company,
                                blank=False,
                                null=False,
                                on_delete=models.CASCADE,
                                related_name='social_links')
    link = models.URLField(blank=False,
                           null=False)

    def __str__(self):
        return '{}: {}'.format(self.company.name, self.link)

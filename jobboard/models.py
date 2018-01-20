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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contract_address = models.CharField(max_length=64, null=True, blank=True)
    first_name = models.CharField(max_length=64, null=False, blank=False)
    middle_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=False, blank=False)
    snails = models.CharField(max_length=32, blank=False, null=False)
    enabled = models.NullBooleanField(default=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + self.snails + ')'


class CurriculumVitae(models.Model):
    title = models.CharField(max_length=255, blank=False, null=True)
    candidate = models.ForeignKey(Candidate, blank=False, null=False, on_delete=models.CASCADE)
    description = models.TextField()
    specializations = models.ManyToManyField(Specialisation)
    keywords = models.ManyToManyField(Keyword)
    salary_from = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.candidate) + ' - ' + self.title


class Employer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contract_address = models.CharField(max_length=64, null=True, blank=True)
    organization = models.CharField(max_length=255, null=False, blank=False)
    inn = models.CharField(max_length=32, null=False, blank=False)
    enabled = models.NullBooleanField(default=True)

    def __str__(self):
        return self.organization + ' (' + self.inn + ')'


class Vacancy(models.Model):
    employer = models.ForeignKey(Employer, blank=False, null=False, on_delete=models.CASCADE)
    contract_address = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    interview_fee = models.CharField(max_length=31, blank=False, null=False, default=0)
    allowed_amount = models.CharField(max_length=31, blank=False, null=False, default=0)
    specializations = models.ManyToManyField(Specialisation)
    keywords = models.ManyToManyField(Keyword)
    salary_from = models.PositiveIntegerField(default=0, blank=True, null=True)
    salary_up_to = models.PositiveIntegerField(blank=True, null=True)
    enabled = models.NullBooleanField(default=True)

    def __str__(self):
        return str(self.employer) + ' ' + self.title


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    txn_hash = models.CharField(max_length=127)
    txn_type = models.CharField(max_length=31)
    obj_id = models.SmallIntegerField(default=0)
    vac_id = models.SmallIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + self.txn_hash


class VacancyTest(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    title = models.CharField(max_length=255)
    question = models.TextField()
    answer = models.CharField(max_length=255)
    max_attempts = models.PositiveIntegerField(default=3)

    def __str__(self):
        return self.title + ' (' + self.vacancy.title + ')'


class CandidateVacancyPassing(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    test = models.ForeignKey(VacancyTest, on_delete=models.CASCADE)
    attempts = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    passed = models.NullBooleanField(default=None)

    def __str__(self):
        return str(self.candidate) + " " + self.test.title + ': ' + str(self.attempts)

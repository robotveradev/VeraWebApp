from django.db import models
from cv.models import Busyness, Schedule


class Vacancy(models.Model):
    employer = models.ForeignKey('jobboard.Employer', blank=False, null=False, on_delete=models.CASCADE)
    contract_address = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    specialisations = models.ManyToManyField('jobboard.Specialisation', blank=True)
    keywords = models.ManyToManyField('jobboard.Keyword', blank=True)
    experience = models.CharField(max_length=10, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    requirement = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255)
    salary_from = models.PositiveIntegerField(default=0, blank=True, null=True)
    salary_up_to = models.PositiveIntegerField(blank=True, null=True)
    busyness = models.ManyToManyField(Busyness, blank=True)
    schedule = models.ManyToManyField(Schedule, blank=True)
    enabled = models.NullBooleanField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.employer) + ' ' + self.title

    class Meta:
        ordering = ('-updated_at',)


class CVOnVacancy(models.Model):
    cv = models.ForeignKey('cv.CurriculumVitae',
                           on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy,
                                on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class VacancyOffer(models.Model):
    vacancy = models.ForeignKey('vacancy.Vacancy',
                                on_delete=models.CASCADE)
    cv = models.ForeignKey('cv.CurriculumVitae',
                           on_delete=models.CASCADE,
                           related_name='offers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True, default='')

    class Meta:
        unique_together = (("vacancy", "cv"),)

    def __str__(self):
        return 'Vacancy offer'

    def refuse(self, description=None):
        self.is_active = False
        self.description = description
        self.save()

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

SEX_CHOICES = (
    ('male', 'male'),
    ('female', 'female'),
)

LANGUAGE_LEVEL_CHOICES = (
    ('Notion', 'Notion'),
    ('Basic', 'Basic'),
    ('Advanced', 'Advanced'),
    ('Professional', 'Professional'),
    ('Bilingual', 'Bilingual'),
)

YEARS = [(i, i) for i in range(1950, now().year)][::-1]

DAYS = [(i, i) for i in range(1, 32)]

MONTHS = (
    (1, _('january')),
    (2, _('febuary')),
    (3, _('march')),
    (4, _('april')),
    (5, _('may')),
    (6, _('june')),
    (7, _('july')),
    (8, _('august')),
    (9, _('september')),
    (10, _('october')),
    (11, _('november')),
    (12, _('december')),
)

WEIGHTS = (
    (0, _('Minor')),
    (1, _('Medium')),
    (2, _('Major')),
)


def current_year():
    return now().year


def current_month():
    return now().month


class Busyness(models.Model):
    title = models.CharField(max_length=127)

    def __str__(self):
        return self.title


class Schedule(models.Model):
    title = models.CharField(max_length=127)

    def __str__(self):
        return self.title


class CurriculumVitae(models.Model):
    candidate = models.ForeignKey('jobboard.Candidate',
                                  on_delete=models.CASCADE,
                                  related_name='cvs')
    image = models.ImageField(blank=True, null=True)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    middle_name = models.CharField(max_length=50, null=True, blank=True, default=None)
    birth_date = models.DateField(blank=True, null=True, default=None)
    sex = models.CharField(max_length=20, choices=SEX_CHOICES)
    city = models.CharField(max_length=127, blank=False, null=False)
    relocation = models.NullBooleanField(default=None)
    official_journey = models.NullBooleanField(default=None)
    experience = models.ManyToManyField('Experience', blank=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    specialisations = models.ManyToManyField('jobboard.Specialisation', blank=True)
    keywords = models.ManyToManyField('jobboard.Keyword', blank=True)
    education = models.ManyToManyField('Education', blank=True)
    languages = models.ManyToManyField('Languages', blank=True)
    level = models.ForeignKey('EducationLevel', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return 'CurriculumVitae: {} {}'.format(self.first_name, self.last_name)

    def get_statistic_url(self):
        return reverse('cvstatistic', kwargs={'pk': self.pk})

    @property
    def title(self):
        return self.position.title if self.position is not None else 'Unpublished CV'

    @property
    def salary_from(self):
        return 'from ' + str(self.position.salary_from) + '$' if self.position is not None else 'Salary not available'

    @property
    def user_field_name(self):
        return 'candidate'


class Position(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    busyness = models.ManyToManyField(Busyness)
    schedule = models.ManyToManyField(Schedule)
    salary_from = models.PositiveIntegerField(default=0, blank=False, null=False)
    carier_start = models.BooleanField(default=False)
    description = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.title


class Experience(models.Model):
    start_year = models.IntegerField(choices=YEARS, default=current_year, verbose_name=_("start year"))
    start_month = models.IntegerField(choices=MONTHS, default=current_month, verbose_name=_("start month"))
    still = models.BooleanField(default=False, verbose_name=_("still in office"))
    end_year = models.IntegerField(choices=YEARS, null=True, blank=True, verbose_name=_("end year"))
    end_month = models.IntegerField(choices=MONTHS, null=True, blank=True, verbose_name=_("end month"))
    organization = models.CharField(max_length=255, blank=False, null=False)
    city = models.CharField(max_length=127, blank=False, null=False)
    position = models.CharField(max_length=127)
    description = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return 'Experience {}'.format(self.position)


class EducationLevel(models.Model):
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=127)

    def __str__(self):
        return self.title


class Education(models.Model):
    institute = models.CharField(max_length=127, blank=True, null=True)
    faculty = models.CharField(max_length=127, blank=True, null=True)
    profession = models.CharField(max_length=127, blank=True, null=True)
    education_from = models.DateField()
    education_to = models.DateField()

    def __str__(self):
        return self.institute or '-'


class Languages(models.Model):
    name = models.CharField(max_length=250)
    level = models.CharField(max_length=20, choices=LANGUAGE_LEVEL_CHOICES)

    def __str__(self):
        return self.name

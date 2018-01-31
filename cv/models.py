from django.contrib.auth.models import User
from django.db import models

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


class Busyness(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Schedule(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Skill(models.Model):
    title = models.CharField(max_length=31)

    def __str__(self):
        return self.title


class CurriculumVitae(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField()
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    middle_name = models.CharField(max_length=50, null=True, blank=True, default=None)
    birth_date = models.DateTimeField(blank=True, null=True, default=None)
    sex = models.CharField(max_length=20, choices=SEX_CHOICES)
    city = models.CharField(max_length=127, blank=False, null=False)
    relocation = models.NullBooleanField(default=None)
    official_journey = models.NullBooleanField(default=None)
    experience = models.ManyToManyField('Experience')
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    skills = models.ManyToManyField('Skill')
    education = models.ManyToManyField('Education')
    languages = models.ManyToManyField('Languages')
    level = models.ForeignKey('EducationLevel', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'CurriculumVitae: {} {}'.format(self.first_name, self.last_name)


class Position(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    busyness = models.ManyToManyField(Busyness)
    schedule = models.ManyToManyField(Schedule)
    salary_from = models.PositiveIntegerField(default=0, blank=False, null=False)
    carier_start = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return self.title


class Experience(models.Model):
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=True, null=True)
    expire = models.BooleanField(default=False)
    organization = models.CharField(max_length=255, blank=False, null=False)
    city = models.CharField(max_length=127, blank=False, null=False)
    position = models.CharField(max_length=127)
    description = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return 'Experience {}'.format(self.position)


class EducationLevel(models.Model):
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Education(models.Model):
    institute = models.CharField(max_length=127, blank=True, null=True)
    faculty = models.CharField(max_length=127, blank=True, null=True)
    profession = models.CharField(max_length=127, blank=True, null=True)
    education_from = models.DateField()
    education_to = models.DateField()

    def __str__(self):
        return self.institute


class Languages(models.Model):
    name = models.CharField(max_length=250)
    level = models.CharField(max_length=20, choices=LANGUAGE_LEVEL_CHOICES)

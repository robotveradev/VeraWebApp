# Generated by Django 2.0.2 on 2018-03-12 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vacancy', '0013_auto_20180306_0836'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidatevacancypassing',
            name='candidate',
        ),
        migrations.RemoveField(
            model_name='candidatevacancypassing',
            name='test',
        ),
        migrations.RemoveField(
            model_name='vacancytest',
            name='vacancy',
        ),
        migrations.DeleteModel(
            name='CandidateVacancyPassing',
        ),
        migrations.DeleteModel(
            name='VacancyTest',
        ),
    ]
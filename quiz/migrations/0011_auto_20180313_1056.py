# Generated by Django 2.0.2 on 2018-03-13 10:56

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('vacancy', '0014_auto_20180312_0823'),
        ('quiz', '0010_auto_20180313_0724'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VacancyTest',
            new_name='VacancyExam',
        ),
    ]
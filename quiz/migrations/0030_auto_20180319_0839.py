# Generated by Django 2.0.2 on 2018-03-19 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0029_vacancyexam_max_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancyexam',
            name='passing_grade',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
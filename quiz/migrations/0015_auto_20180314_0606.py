# Generated by Django 2.0.2 on 2018-03-14 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0014_auto_20180314_0542'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='is_valid',
        ),
        migrations.AlterField(
            model_name='answer',
            name='weight',
            field=models.SmallIntegerField(default=1, help_text='Value from -100 to 100'),
        ),
        migrations.AlterField(
            model_name='question',
            name='weight',
            field=models.SmallIntegerField(default=1, help_text='Value from -100 to 100'),
        ),
    ]
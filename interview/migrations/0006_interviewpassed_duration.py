# Generated by Django 2.0.3 on 2018-08-15 07:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('interview', '0005_auto_20180809_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewpassed',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
    ]

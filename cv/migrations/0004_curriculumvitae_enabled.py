# Generated by Django 2.0.3 on 2018-04-06 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0003_curriculumvitae_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculumvitae',
            name='enabled',
            field=models.NullBooleanField(default=False),
        ),
    ]

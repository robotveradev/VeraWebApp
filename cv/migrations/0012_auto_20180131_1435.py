# Generated by Django 2.0 on 2018-01-31 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0011_auto_20180131_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculumvitae',
            name='official_journey',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='curriculumvitae',
            name='relocation',
            field=models.NullBooleanField(default=None),
        ),
    ]

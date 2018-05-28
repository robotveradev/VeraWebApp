# Generated by Django 2.0.3 on 2018-04-19 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobboard', '0003_auto_20180403_1132'),
    ]

    operations = [
        migrations.CreateModel(
            name='InviteCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='92MJ45VRB4DHW90F11ILSACXNIR5P8QN', max_length=32, unique=True, verbose_name='code')),
                ('expired', models.BooleanField(default=False)),
            ],
        ),
    ]
# Generated by Django 2.0.3 on 2018-04-11 07:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0004_curriculumvitae_enabled'),
        ('vacancy', '0006_auto_20180406_0826'),
        ('interview', '0003_dialog_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cv.CurriculumVitae')),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interviews', to='vacancy.Vacancy')),
            ],
        ),
        migrations.RemoveField(
            model_name='dialog',
            name='opponent',
        ),
        migrations.RemoveField(
            model_name='dialog',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='message',
            name='dialog',
        ),
        migrations.DeleteModel(
            name='Dialog',
        ),
        migrations.AddField(
            model_name='actioninterview',
            name='interview',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='action', to='interview.Interview'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='interview',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='interview.Interview'),
            preserve_default=False,
        ),
    ]

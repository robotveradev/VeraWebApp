# Generated by Django 2.0.2 on 2018-03-15 15:33

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jobboard', '0033_auto_20180301_1146'),
        ('quiz', '0021_candidatevacancypassing_answers'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamPassing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answers', jsonfield.fields.JSONField()),
                ('points', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='jobboard.Candidate')),
                ('test', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz.VacancyExam')),
            ],
        ),
        migrations.RemoveField(
            model_name='candidatevacancypassing',
            name='candidate',
        ),
        migrations.RemoveField(
            model_name='candidatevacancypassing',
            name='test',
        ),
        migrations.DeleteModel(
            name='CandidateVacancyPassing',
        ),
    ]
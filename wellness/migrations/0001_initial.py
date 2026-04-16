# Generated migration for Wellness app

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SurveyResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('mood_score', models.PositiveSmallIntegerField(default=0)),
                ('anxiety_score', models.PositiveSmallIntegerField(default=0)),
                ('sleep_score', models.PositiveSmallIntegerField(default=0)),
                ('energy_score', models.PositiveSmallIntegerField(default=0)),
                ('concentration_score', models.PositiveSmallIntegerField(default=0)),
                ('hopelessness_score', models.PositiveSmallIntegerField(default=0)),
                ('support_score', models.PositiveSmallIntegerField(default=0)),
                ('total_score', models.PositiveSmallIntegerField(default=0)),
                ('risk_level', models.CharField(blank=True, max_length=32)),
                ('recommendation', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('mood', 'Mood / Depression'), ('anxiety', 'Anxiety'), ('sleep', 'Sleep'), ('energy', 'Energy'), ('concentration', 'Concentration'), ('hopelessness', 'Hopelessness'), ('support', 'Social/Emotional Support')], max_length=32)),
                ('text', models.TextField()),
                ('order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
    ]

# Generated by Django 5.1.2 on 2024-11-09 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0036_rename_scores_player_league_scores'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='league_scores',
        ),
    ]
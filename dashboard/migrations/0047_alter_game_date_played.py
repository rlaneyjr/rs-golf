# Generated by Django 5.1.2 on 2024-12-02 19:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0046_remove_player_previous_handicap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='date_played',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

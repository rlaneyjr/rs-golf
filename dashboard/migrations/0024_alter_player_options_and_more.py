# Generated by Django 4.2.5 on 2024-03-10 14:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0023_player_email"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="player",
            options={"ordering": ["first_name", "last_name"]},
        ),
        migrations.RemoveField(
            model_name="playermembership",
            name="current_handicap",
        ),
        migrations.AddField(
            model_name="playermembership",
            name="game_handicap",
            field=models.DecimalField(
                blank=True, decimal_places=1, default=None, max_digits=3, null=True
            ),
        ),
    ]

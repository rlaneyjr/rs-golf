# Generated by Django 4.2.5 on 2024-01-08 13:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0012_game_score"),
    ]

    operations = [
        migrations.AddField(
            model_name="playermembership",
            name="in_skins",
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 4.2.5 on 2024-03-22 13:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "dashboard",
            "0027_alter_holescore_options_playermembership_game_points_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="holescore",
            options={"ordering": ["player", "hole"], "verbose_name_plural": "scores"},
        ),
        migrations.RemoveField(
            model_name="holescore",
            name="score",
        ),
        migrations.AddField(
            model_name="holescore",
            name="points",
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="holescore",
            name="strokes",
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
    ]

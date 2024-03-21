# Generated by Django 4.2.5 on 2024-03-21 01:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0026_player_previous_handicap"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="holescore",
            options={
                "ordering": ["hole", "score", "player"],
                "verbose_name_plural": "scores",
            },
        ),
        migrations.AddField(
            model_name="playermembership",
            name="game_points",
            field=models.SmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="playermembership",
            name="game_score",
            field=models.SmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="game",
            name="game_type",
            field=models.CharField(
                choices=[
                    ("best-ball", "Best Ball"),
                    ("stroke", "Stroke"),
                    ("stableford", "Stableford"),
                ],
                default="stableford",
                max_length=32,
            ),
        ),
    ]

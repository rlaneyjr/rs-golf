# Generated by Django 4.2.5 on 2023-10-24 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("home", "0008_alter_game_holes_played_alter_hole_order_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="hole",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="player",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="golfcourse",
            name="initials",
            field=models.CharField(
                default="GC", max_length=5, verbose_name="Course Initials"
            ),
        ),
        migrations.AddField(
            model_name="hole",
            name="handicap",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Hole 1"),
                    (2, "Hole 2"),
                    (3, "Hole 3"),
                    (4, "Hole 4"),
                    (5, "Hole 5"),
                    (6, "Hole 6"),
                    (7, "Hole 7"),
                    (8, "Hole 8"),
                    (9, "Hole 9"),
                    (10, "Hole 10"),
                    (11, "Hole 11"),
                    (12, "Hole 12"),
                    (13, "Hole 13"),
                    (14, "Hole 14"),
                    (15, "Hole 15"),
                    (16, "Hole 16"),
                    (17, "Hole 17"),
                    (18, "Hole 18"),
                ],
                default=1,
            ),
        ),
        migrations.AddField(
            model_name="player",
            name="handicap",
            field=models.DecimalField(decimal_places=1, default=10.0, max_digits=3),
        ),
        migrations.AlterField(
            model_name="game",
            name="holes_played",
            field=models.CharField(
                choices=[("9", "9 Holes"), ("18", "18 Holes")],
                default=("18", "18 Holes"),
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="status",
            field=models.CharField(
                choices=[
                    ("setup", "Setup"),
                    ("active", "Active"),
                    ("completed", "Completed"),
                    ("not_finished", "Not Finished"),
                ],
                default=("setup", "Setup"),
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="golfcourse",
            name="hole_count",
            field=models.CharField(
                choices=[("9", "9 Holes"), ("18", "18 Holes")],
                default=("18", "18 Holes"),
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="golfcourse",
            name="state",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name="hole",
            name="name",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name="hole",
            name="order",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Hole 1"),
                    (2, "Hole 2"),
                    (3, "Hole 3"),
                    (4, "Hole 4"),
                    (5, "Hole 5"),
                    (6, "Hole 6"),
                    (7, "Hole 7"),
                    (8, "Hole 8"),
                    (9, "Hole 9"),
                    (10, "Hole 10"),
                    (11, "Hole 11"),
                    (12, "Hole 12"),
                    (13, "Hole 13"),
                    (14, "Hole 14"),
                    (15, "Hole 15"),
                    (16, "Hole 16"),
                    (17, "Hole 17"),
                    (18, "Hole 18"),
                ],
                default=1,
            ),
        ),
        migrations.AlterField(
            model_name="hole",
            name="par",
            field=models.PositiveSmallIntegerField(
                choices=[(3, "Par 3"), (4, "Par 4"), (5, "Par 5")], default=3
            ),
        ),
        migrations.AlterField(
            model_name="player",
            name="user_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="tee",
            name="name",
            field=models.CharField(
                choices=[
                    ("black", "Black"),
                    ("blue", "Blue"),
                    ("gold", "Gold"),
                    ("white", "White"),
                    ("red", "Red"),
                ],
                default=("blue", "Blue"),
                max_length=5,
                verbose_name="Tee Color",
            ),
        ),
        migrations.AlterField(
            model_name="teetime",
            name="holes_to_play",
            field=models.CharField(
                choices=[("9", "9 Holes"), ("18", "18 Holes")],
                default=("18", "18 Holes"),
                max_length=2,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="hole",
            unique_together={("course", "order", "handicap")},
        ),
        migrations.AlterUniqueTogether(
            name="player",
            unique_together={("name", "user_account")},
        ),
    ]

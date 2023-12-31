# Generated by Django 4.2.5 on 2023-10-10 13:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_played", models.DateTimeField(blank=True, null=True)),
                (
                    "holes_played",
                    models.CharField(
                        choices=[("9", "9 Holes"), ("18", "18 Holes")],
                        default="9 Holes",
                        max_length=64,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("setup", "Setup"),
                            ("active", "Active"),
                            ("completed", "Completed"),
                            ("not_finished", "Not Finished"),
                        ],
                        default="setup",
                        max_length=64,
                    ),
                ),
                ("league_game", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="GolfCourse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                (
                    "hole_count",
                    models.CharField(
                        choices=[("9", "9 Holes"), ("18", "18 Holes")],
                        default="9",
                        max_length=64,
                    ),
                ),
                ("tee_time_link", models.URLField(blank=True)),
                ("website_link", models.URLField(blank=True)),
                ("city", models.CharField(blank=True, max_length=128)),
                ("state", models.CharField(blank=True, max_length=128)),
                ("zip_code", models.CharField(blank=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="Hole",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("nickname", models.CharField(blank=True, max_length=128)),
                ("par", models.IntegerField(default=3)),
                ("order", models.IntegerField(default=0)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="home.golfcourse",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                (
                    "added_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="added_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_account",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("name", "added_by")},
            },
        ),
        migrations.CreateModel(
            name="TeeTime",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tee_time", models.DateTimeField()),
                (
                    "holes_to_play",
                    models.CharField(
                        choices=[("9", "9 Holes"), ("18", "18 Holes")],
                        default="9",
                        max_length=64,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="home.golfcourse",
                    ),
                ),
                ("players", models.ManyToManyField(to="home.player")),
            ],
        ),
        migrations.CreateModel(
            name="Tee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("distance", models.CharField(max_length=10)),
                (
                    "hole",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.hole"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PlayerGameLink",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.game"
                    ),
                ),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.player"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HoleScore",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.IntegerField(default=0)),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="home.playergamelink",
                    ),
                ),
                (
                    "hole",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.hole"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="game",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="home.golfcourse"
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="players",
            field=models.ManyToManyField(
                through="home.PlayerGameLink", to="home.player"
            ),
        ),
    ]

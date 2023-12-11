# Generated by Django 4.2.5 on 2023-12-05 13:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="added_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="added_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="player",
            name="user_account",
            field=models.OneToOneField(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="holescore",
            name="hole",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dashboard.hole"
            ),
        ),
        migrations.AddField(
            model_name="holescore",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="dashboard.playermembership",
            ),
        ),
        migrations.AddField(
            model_name="hole",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dashboard.golfcourse"
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="dashboard.golfcourse"
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="players",
            field=models.ManyToManyField(
                through="dashboard.PlayerMembership", to="dashboard.player"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="tee",
            unique_together={("color", "hole")},
        ),
        migrations.AlterUniqueTogether(
            name="player",
            unique_together={("name", "handicap", "user_account")},
        ),
        migrations.AlterUniqueTogether(
            name="hole",
            unique_together={("name", "course", "order", "handicap")},
        ),
    ]

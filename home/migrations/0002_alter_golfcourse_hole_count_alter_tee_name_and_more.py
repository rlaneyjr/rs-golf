# Generated by Django 4.2.5 on 2023-10-15 13:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="golfcourse",
            name="hole_count",
            field=models.CharField(
                choices=[("9", "9 Holes"), ("18", "18 Holes")],
                default="9 Holes",
                max_length=64,
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
                default="Black",
                max_length=64,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="tee",
            unique_together={("name", "hole")},
        ),
    ]

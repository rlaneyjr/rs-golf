# Generated by Django 4.2.5 on 2023-10-16 00:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0007_remove_hole_photo_alter_golfcourse_card_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="holes_played",
            field=models.CharField(
                choices=[("9", "9 Holes"), ("18", "18 Holes")],
                default="9 Holes",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="hole",
            name="order",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="hole",
            name="par",
            field=models.CharField(
                choices=[("3", "Three"), ("4", "Four"), ("5", "Five")],
                default="3",
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="holescore",
            name="score",
            field=models.IntegerField(
                choices=[
                    ("-3", "Albatross"),
                    ("-2", "Eagle"),
                    ("-1", "Birdie"),
                    ("0", "Par"),
                    ("1", "Bogey"),
                    ("2", "Double Bogey"),
                    ("3", "Triple Bogey"),
                ],
                default=("0", "Par"),
            ),
        ),
        migrations.AlterField(
            model_name="tee",
            name="distance",
            field=models.CharField(max_length=3),
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
                max_length=5,
            ),
        ),
        migrations.AlterField(
            model_name="teetime",
            name="holes_to_play",
            field=models.CharField(
                choices=[("9", "9 Holes"), ("18", "18 Holes")],
                default="9",
                max_length=2,
            ),
        ),
    ]

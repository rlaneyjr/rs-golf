# Generated by Django 4.2.5 on 2023-10-15 18:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0003_golfcourse_card_golfcourse_overview_hole_photo_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="golfcourse",
            name="card",
            field=models.ImageField(
                blank=True, default=None, null=True, upload_to="static/images"
            ),
        ),
        migrations.AlterField(
            model_name="golfcourse",
            name="overview",
            field=models.ImageField(
                blank=True, default=None, null=True, upload_to="static/images"
            ),
        ),
        migrations.AlterField(
            model_name="hole",
            name="photo",
            field=models.ImageField(
                blank=True, default=None, null=True, upload_to="static/images"
            ),
        ),
        migrations.AlterField(
            model_name="player",
            name="photo",
            field=models.ImageField(
                blank=True, default=None, null=True, upload_to="static/images"
            ),
        ),
    ]

# Generated by Django 4.2.5 on 2023-10-15 19:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0006_alter_golfcourse_card_alter_golfcourse_overview_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hole",
            name="photo",
        ),
        migrations.AlterField(
            model_name="golfcourse",
            name="card",
            field=models.ImageField(
                blank=True, default=None, null=True, upload_to="images"
            ),
        ),
        migrations.AlterField(
            model_name="golfcourse",
            name="overview",
            field=models.ImageField(
                blank=True, default=None, null=True, upload_to="images"
            ),
        ),
        migrations.AlterField(
            model_name="player",
            name="photo",
            field=models.ImageField(
                blank=True, default=None, null=True, upload_to="images"
            ),
        ),
    ]

# Generated by Django 4.2.5 on 2023-11-08 13:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0017_alter_teetime_tee_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="teetime",
            name="tee_time",
            field=models.DateTimeField(default="11-08-2023 08:08"),
        ),
    ]

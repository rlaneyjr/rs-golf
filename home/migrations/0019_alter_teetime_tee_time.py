# Generated by Django 4.2.5 on 2023-11-09 12:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0018_alter_teetime_tee_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="teetime",
            name="tee_time",
            field=models.DateTimeField(default="11-09-2023 07:33"),
        ),
    ]

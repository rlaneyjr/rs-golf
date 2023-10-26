# Generated by Django 4.2.5 on 2023-10-08 12:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="user_type",
            field=models.CharField(
                choices=[
                    ("PLAYER", "Player"),
                    ("STAFF", "Staff"),
                    ("SUPERUSER", "Superuser"),
                ],
                default="PLAYER",
                help_text="Displays the users current user type.",
                max_length=50,
                verbose_name="Type",
            ),
        ),
    ]

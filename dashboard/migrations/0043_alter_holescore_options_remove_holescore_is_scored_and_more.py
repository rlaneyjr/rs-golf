# Generated by Django 5.1.2 on 2024-11-24 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0042_remove_holescore_score_holescore_is_scored'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='holescore',
            options={'ordering': ['player', 'hole', 'strokes'], 'verbose_name_plural': 'scores'},
        ),
        migrations.RemoveField(
            model_name='holescore',
            name='is_scored',
        ),
        migrations.RemoveField(
            model_name='holescore',
            name='points',
        ),
        migrations.AlterUniqueTogether(
            name='tee',
            unique_together={('hole', 'color')},
        ),
    ]
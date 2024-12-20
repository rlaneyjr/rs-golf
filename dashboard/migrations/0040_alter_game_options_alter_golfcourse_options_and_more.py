# Generated by Django 5.1.2 on 2024-11-20 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0039_alter_player_options_alter_tee_color_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'get_latest_by': 'date_played', 'ordering': ['date_played', 'status'], 'verbose_name_plural': 'games'},
        ),
        migrations.AlterModelOptions(
            name='golfcourse',
            options={'ordering': ['state', 'city']},
        ),
        migrations.AlterModelOptions(
            name='hole',
            options={'ordering': ['course', 'order']},
        ),
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ['-handicap'], 'verbose_name_plural': 'players'},
        ),
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['-handicap'], 'verbose_name_plural': 'teams'},
        ),
        migrations.AlterModelOptions(
            name='tee',
            options={'ordering': ['hole', '-distance']},
        ),
        migrations.AlterModelOptions(
            name='teetime',
            options={'ordering': ['tee_time'], 'verbose_name_plural': 'tee_times'},
        ),
        migrations.AlterUniqueTogether(
            name='golfcourse',
            unique_together={('name', 'city', 'state')},
        ),
    ]

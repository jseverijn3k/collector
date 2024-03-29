# Generated by Django 5.0.2 on 2024-03-24 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_collections', '0011_track_musicbrainz_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artist',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='release',
            options={'ordering': ['name', 'artist']},
        ),
        migrations.AlterModelOptions(
            name='track',
            options={'ordering': ['release', 'position']},
        ),
        migrations.AddField(
            model_name='track',
            name='number',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]

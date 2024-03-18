# Generated by Django 5.0.2 on 2024-03-18 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_collections', '0004_release_cd_tracks_release_dvd_tracks'),
    ]

    operations = [
        migrations.AddField(
            model_name='cover_art',
            name='cover_art_size',
            field=models.CharField(blank=True, default='full', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='cover_art',
            name='cover_art_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='cover_art',
            name='musicbrainz_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]

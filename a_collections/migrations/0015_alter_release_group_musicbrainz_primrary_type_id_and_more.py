# Generated by Django 5.0.2 on 2024-03-28 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_collections', '0014_release_group_secondary_type_ids_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='release_group',
            name='musicbrainz_primrary_type_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='release_group',
            name='musicbrainz_type_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='release_group',
            name='secondary_type_ids',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
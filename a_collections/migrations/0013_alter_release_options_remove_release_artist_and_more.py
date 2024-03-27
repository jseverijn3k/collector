# Generated by Django 5.0.2 on 2024-03-27 06:54

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_collections', '0012_alter_artist_options_alter_release_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='release',
            options={'ordering': ['name']},
        ),
        migrations.RemoveField(
            model_name='release',
            name='artist',
        ),
        migrations.RemoveField(
            model_name='release',
            name='release_year',
        ),
        migrations.CreateModel(
            name='Release_Group',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('musicbrainz_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('musicbrainz_type_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('musicbrainz_primrary_type_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('primrary_type', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('first_release_date', models.DateField()),
                ('artist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='artists', to='a_collections.artist')),
            ],
            options={
                'ordering': ['name', 'artist'],
            },
        ),
        migrations.AddField(
            model_name='release',
            name='release_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='release_group', to='a_collections.release_group'),
        ),
    ]
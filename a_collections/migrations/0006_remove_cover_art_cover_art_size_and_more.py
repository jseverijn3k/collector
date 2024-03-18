# Generated by Django 5.0.2 on 2024-03-18 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_collections', '0005_cover_art_cover_art_size_cover_art_cover_art_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cover_art',
            name='cover_art_size',
        ),
        migrations.AddField(
            model_name='cover_art',
            name='image_small_url',
            field=models.URLField(default=1),
            preserve_default=False,
        ),
    ]
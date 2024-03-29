# Generated by Django 5.0.2 on 2024-03-23 13:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_collections', '0009_cover_art_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('position', models.IntegerField()),
                ('duration', models.CharField(blank=True, max_length=20, null=True)),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='a_collections.release')),
            ],
        ),
    ]

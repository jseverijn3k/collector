# Generated by Django 5.0.2 on 2024-03-18 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_collections', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='barcode',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='release',
            name='date',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='release',
            name='language',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='release',
            name='status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]

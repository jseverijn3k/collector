# Generated by Django 5.0.2 on 2024-03-20 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_collections', '0007_record_label_musicbrainz_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collection',
            old_name='type',
            new_name='condition',
        ),
        migrations.AddField(
            model_name='collection',
            name='date_added',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='description',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
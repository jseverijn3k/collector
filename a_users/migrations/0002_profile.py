# Generated by Django 5.0.2 on 2024-03-11 14:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('realname', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(max_length=254, null=True, unique=True)),
                ('location', models.CharField(blank=True, max_length=20, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

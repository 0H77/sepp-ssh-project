# Generated by Django 5.1.4 on 2024-12-12 02:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cartapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='university_name',
            new_name='address',
        ),
    ]

# Generated by Django 5.1.4 on 2024-12-29 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_profile_additional_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='additional_info',
        ),
    ]

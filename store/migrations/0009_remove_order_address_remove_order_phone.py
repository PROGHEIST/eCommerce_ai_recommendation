# Generated by Django 5.1.5 on 2025-02-15 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_delete_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='phone',
        ),
    ]

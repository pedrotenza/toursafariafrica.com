# Generated by Django 5.2 on 2025-06-21 08:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_safari_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='safari',
            name='date',
        ),
    ]

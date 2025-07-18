# Generated by Django 5.2 on 2025-06-23 11:11

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_provider_safari_provider'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='booking_datetime',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='client_age',
            field=models.PositiveIntegerField(default=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='client_nationality',
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='client_phone',
            field=models.CharField(default=0, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='provider_response_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

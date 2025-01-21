# Generated by Django 5.1.3 on 2025-01-16 21:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxi', '0004_alter_consumer_options_alter_driver_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ride',
            options={'ordering': ['driver', '-date_created'], 'verbose_name_plural': 'Поездки'},
        ),
        migrations.AddField(
            model_name='ride',
            name='addresses',
            field=models.ManyToManyField(through='taxi.RideAddressesQueue', to='taxi.address'),
        ),
        migrations.AlterField(
            model_name='rideaddressesqueue',
            name='ride',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taxi.ride'),
        ),
    ]

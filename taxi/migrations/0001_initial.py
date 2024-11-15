# Generated by Django 5.1.3 on 2024-11-08 11:46

import datetime
import django.db.models.deletion
import taxi.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='Address name')),
            ],
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Car Number')),
                ('color', models.CharField(max_length=63, verbose_name='Color')),
                ('make', models.CharField(max_length=100, verbose_name='Make')),
                ('series', models.CharField(max_length=100, verbose_name='Series')),
                ('is_ready', models.BooleanField(default=True, verbose_name='Ready to use')),
                ('comfort_class', models.CharField(choices=[('comfort_plus', 'Comfort Plus'), ('business', 'Business'), ('together', 'Together'), ('comfort', 'Comfort'), ('econom', 'Econom')], max_length=50, verbose_name='Comfort class')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=511, verbose_name='City')),
            ],
        ),
        migrations.CreateModel(
            name='Consumer',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=511, verbose_name='District')),
            ],
        ),
        migrations.CreateModel(
            name='Street',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=511, verbose_name='Street name')),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('current_car', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='taxi.car')),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='taxi.district')),
            ],
        ),
        migrations.CreateModel(
            name='ConsumerRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rates', to='taxi.consumer')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rates_authored', to='taxi.driver')),
            ],
            bases=(models.Model, taxi.models.Rate),
        ),
        migrations.CreateModel(
            name='DriverRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rates_authored', to='taxi.consumer')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rates', to='taxi.driver')),
            ],
            bases=(models.Model, taxi.models.Rate),
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=datetime.datetime.now)),
                ('date_ended', models.DateTimeField(default=None, null=True)),
                ('consumer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rides', to='taxi.consumer')),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rides', to='taxi.driver')),
            ],
            options={
                'ordering': ['date_created'],
                'unique_together': {('consumer', 'driver', 'date_created')},
            },
        ),
        migrations.CreateModel(
            name='RideAddressesQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('date_created', models.DateTimeField(default=datetime.datetime.now)),
                ('date_ended', models.DateTimeField(default=None, null=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rides', to='taxi.address')),
                ('ride', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adresses', to='taxi.ride')),
            ],
            options={
                'ordering': ['order', 'date_ended', 'date_created'],
                'unique_together': {('ride', 'address')},
            },
        ),
    ]

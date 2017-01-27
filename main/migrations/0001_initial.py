# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-27 00:54
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlockGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geoid', models.CharField(max_length=12)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('listing_url', models.CharField(max_length=512)),
                ('scrape_id', models.BigIntegerField()),
                ('last_scraped', models.DateField()),
                ('description', models.TextField()),
                ('host_id', models.BigIntegerField()),
                ('host_name', models.CharField(max_length=512)),
                ('host_since', models.DateField()),
                ('host_is_superhost', models.BooleanField()),
                ('host_identity_verified', models.BooleanField()),
                ('neighbourhood_cleansed', models.CharField(max_length=512)),
                ('property_type', models.CharField(max_length=512)),
                ('room_type', models.CharField(max_length=512)),
                ('accommodates', models.IntegerField()),
                ('bathrooms', models.FloatField()),
                ('bedrooms', models.FloatField()),
                ('bed_type', models.CharField(max_length=512)),
                ('amenities', models.TextField()),
                ('price', models.FloatField()),
                ('minimum_nights', models.IntegerField()),
                ('availability_365', models.IntegerField()),
                ('number_of_reviews', models.IntegerField()),
                ('reviews_per_month', models.FloatField()),
                ('street', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Neighborhood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, unique=True)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Zipcode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zipcode', models.CharField(max_length=5)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
        ),
        migrations.AddField(
            model_name='listing',
            name='neighborhood',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Neighborhood'),
        ),
    ]

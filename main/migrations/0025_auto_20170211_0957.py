# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-11 09:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20170208_0957'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('reviewer_id', models.BigIntegerField()),
                ('comments', models.TextField(null=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Listing')),
            ],
        ),
        migrations.AlterModelOptions(
            name='amenity',
            options={'ordering': ('name',), 'verbose_name_plural': 'amenities'},
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-28 02:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockgroup',
            name='area_land',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blockgroup',
            name='area_water',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='zipcode',
            name='area_land',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='zipcode',
            name='area_water',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-12 12:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20170211_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='estimated_revenue_per_month',
            field=models.FloatField(default=0),
        ),
    ]
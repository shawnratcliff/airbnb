# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-23 02:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20170123_0228'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='neighbourhood_cleansed',
            field=models.CharField(default='', max_length=512),
            preserve_default=False,
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-08 01:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20170206_0407'),
    ]

    operations = [
        migrations.AddField(
            model_name='crime',
            name='category',
            field=models.CharField(max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='crime',
            name='data_source',
            field=models.CharField(choices=[('LAPD', 'Los Angeles Police Department'), ('LACS', 'Los Angeles County Sheriff')], db_index=True, default='LAPD', max_length=16),
            preserve_default=False,
        ),
    ]
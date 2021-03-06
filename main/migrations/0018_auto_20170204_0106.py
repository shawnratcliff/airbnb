# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-04 01:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20170204_0105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockgroup',
            name='geoid',
            field=models.CharField(max_length=12),
        ),
        migrations.AlterField(
            model_name='zipcode',
            name='geoid',
            field=models.CharField(max_length=5),
        ),
        migrations.AddField(
            model_name='blockgroup',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='zipcode',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]

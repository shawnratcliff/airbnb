# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-29 12:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20170129_1211'),
    ]

    operations = [
        migrations.RenameField(
            model_name='zipcode',
            old_name='zipcode',
            new_name='geoid',
        ),
    ]
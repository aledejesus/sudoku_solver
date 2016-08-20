# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-20 16:35
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solver', '0006_auto_20160812_0419'),
    ]

    operations = [
        migrations.AddField(
            model_name='sudokupuzzle',
            name='missing_vals_pos',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=2), blank=True, default=[], null=True, size=None),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-11-12 22:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solver', '0003_auto_20170201_0106'),
    ]

    operations = [
        migrations.AddField(
            model_name='sudokupuzzle',
            name='correct',
            field=models.BooleanField(default=True),
        ),
    ]

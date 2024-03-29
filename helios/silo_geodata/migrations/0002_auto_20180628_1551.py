# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-28 15:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('silo_geodata', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipcache',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'TYPE_BUSINESS'), (2, 'TYPE_CAFE'), (3, 'TYPE_CELLULAR'), (4, 'TYPE_COLLEGE'), (5, 'TYPE_CDN'), (6, 'TYPE_DIALUP'), (7, 'TYPE_GOVERNMENT'), (8, 'TYPE_HOSTING'), (9, 'TYPE_LIBRARY'), (10, 'TYPE_MILITARY'), (11, 'TYPE_RESIDENTIAL'), (12, 'TYPE_ROUTER'), (13, 'TYPE_SCHOOL'), (14, 'TYPE_SPIDER'), (15, 'TYPE_TRAVELER')], db_index=True, null=True),
        ),
    ]

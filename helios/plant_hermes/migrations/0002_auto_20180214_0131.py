# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-14 01:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plant_hermes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='journaluser',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='usr_source',
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='journaluser',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='usr_target',
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='journalout',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='trans_out',
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='journalin',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='trans_in',
                                    to=settings.AUTH_USER_MODEL),
        ),
    ]

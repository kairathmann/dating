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
        ('plant_eos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentnotice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eos_sent',
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eos_queued',
                                    to=settings.AUTH_USER_MODEL),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-14 01:31
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StashedAsset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(db_index=True, max_length=16)),
                ('engine', models.CharField(db_index=True, max_length=16)),
                ('worker', models.CharField(db_index=True, max_length=32)),
                ('state', models.CharField(
                    choices=[(b'NONE', b'STATE_NONE'), (b'WAITING', b'STATE_WAITING'), (b'STARTED', b'STATE_STARTED'),
                             (b'DONE', b'STATE_DONE'), (b'FAILED', b'STATE_FAILED')], db_index=True, max_length=16)),
                ('input', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('output', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('progress', models.PositiveSmallIntegerField(db_index=True)),
                ('created', models.DateTimeField(db_index=True)),
                ('updated', models.DateTimeField(db_index=True)),
                ('requester',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requester_stashed_assets',
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
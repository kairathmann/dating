# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-14 01:31
from __future__ import unicode_literals

import datetime
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sys_base.fields.field_fulltext
import sys_base.hsm.model


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(db_index=True, default=datetime.datetime.now)),
                ('bid_price',
                 models.DecimalField(db_index=True, decimal_places=8, default=Decimal('0E-8'), max_digits=20)),
                ('hsm_sig', models.BinaryField(null=True)),
                ('last_update', models.DateTimeField(db_index=True)),
                ('bid_status', models.SmallIntegerField(
                    choices=[(1, b'BID_WINNING'), (2, b'BID_LOSING'), (3, b'BID_WON'), (4, b'BID_LOST'),
                             (5, b'BID_ACCEPTED'), (6, b'BID_TIMEOUT')], db_index=True)),
                ('sender_status',
                 models.SmallIntegerField(choices=[(1, b'STATUS_PENDING'), (2, b'STATUS_CURRENT')], db_index=True)),
                ('recipient_status',
                 models.SmallIntegerField(choices=[(1, b'STATUS_PENDING'), (2, b'STATUS_CURRENT')], db_index=True)),
                ('subject', models.CharField(max_length=255)),
                ('fulltext',
                 sys_base.fields.field_fulltext.VectorField(db_index=True, default=b'', editable=False, null=True,
                                                            serialize=False)),
                ('last_message_sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT,
                                                          to=settings.AUTH_USER_MODEL)),
                ('recipient',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='received_conversations',
                                   to=settings.AUTH_USER_MODEL)),
                ('sender',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sent_conversations',
                                   to=settings.AUTH_USER_MODEL)),
            ],
            bases=(sys_base.hsm.model.SecureModel, models.Model),
        ),
        migrations.CreateModel(
            name='IntroSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(default=datetime.datetime.now)),
                ('min_bid',
                 models.DecimalField(db_index=True, decimal_places=8, default=Decimal('0E-8'), max_digits=20)),
                ('max_daily_intros', models.PositiveSmallIntegerField(db_index=True, default=1)),
                ('next_check', models.DateTimeField(db_index=True, default=datetime.datetime.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbox_settings',
                                           to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_time', models.DateTimeField(db_index=True, null=True)),
                ('body', models.TextField()),
                ('fulltext',
                 sys_base.fields.field_fulltext.VectorField(db_index=True, default=b'', editable=False, null=True,
                                                            serialize=False)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages',
                                                   to='silo_message.Conversation')),
                ('recipient',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages',
                                   to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages',
                                             to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='conversation',
            unique_together=set([('sender', 'recipient')]),
        ),
        migrations.AlterIndexTogether(
            name='conversation',
            index_together=set([('sender', 'recipient')]),
        ),
    ]

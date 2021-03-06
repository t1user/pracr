# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-06 18:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0059_auto_20180105_1623'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salary',
            name='total_annual',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='total_monthly',
        ),
        migrations.AlterField(
            model_name='salary',
            name='bonus_gross_annual',
            field=models.PositiveIntegerField(editable=False, null=True, verbose_name='premia brutto rocznie'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='bonus_gross_input_period',
            field=models.PositiveIntegerField(editable=False, null=True, verbose_name='premia brutto'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='bonus_input',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='premia'),
        ),
    ]

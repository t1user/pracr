# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-01 18:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0044_auto_20171130_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='products',
        ),
        migrations.AlterField(
            model_name='company',
            name='isin',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='ISIN'),
        ),
        migrations.AlterField(
            model_name='company',
            name='sectors',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='sektory'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-07 17:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0060_auto_20180106_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='got_offer',
            field=models.BooleanField(verbose_name='dostał ofertę?'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='questions',
            field=models.TextField(blank=True, null=True, verbose_name='proces i pytania'),
        ),
    ]

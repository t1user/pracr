# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-24 15:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0016_auto_20170824_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='linkedin_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]

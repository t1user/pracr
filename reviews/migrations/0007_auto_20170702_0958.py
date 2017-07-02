# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-02 07:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0006_auto_20170701_1910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='website',
            field=models.URLField(unique=True),
        ),
    ]

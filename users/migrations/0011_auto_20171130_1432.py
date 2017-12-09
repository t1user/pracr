# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-30 13:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20171121_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='sex',
            field=models.CharField(blank=True, choices=[('K', 'Kobieta'), ('M', 'Mężczyzna')], default=None, max_length=1, null=True, verbose_name='płeć'),
        ),
    ]
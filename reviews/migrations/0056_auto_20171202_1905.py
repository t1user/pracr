# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-02 18:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0055_auto_20171202_1904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='sectors',
            field=models.TextField(blank=True, null=True, verbose_name='sektory'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-06 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0019_auto_20170825_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='department',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='interview',
            name='difficulty',
            field=models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=None, verbose_name='trudność'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='got_offer',
            field=models.BooleanField(choices=[(True, 'Tak'), (False, 'Nie')], default=None, verbose_name='czy dostał ofertę'),
        ),
        migrations.AlterField(
            model_name='review',
            name='comment',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='salary',
            name='bonus_period',
            field=models.CharField(choices=[('M', 'miesięcznie'), ('K', 'kwartalnie'), ('R', 'rocznie'), ('G', 'na godzinę')], default='R', max_length=1, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='salary',
            name='period',
            field=models.CharField(choices=[('M', 'miesięcznie'), ('K', 'kwartalnie'), ('R', 'rocznie'), ('G', 'na godzinę')], default='M', max_length=1, verbose_name=''),
        ),
    ]

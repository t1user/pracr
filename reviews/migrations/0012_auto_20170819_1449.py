# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-19 12:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0011_auto_20170707_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='advancement',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='Możliwości rozwoju'),
        ),
        migrations.AlterField(
            model_name='company',
            name='compensation',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='Zarobki'),
        ),
        migrations.AlterField(
            model_name='company',
            name='environment',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='Atmosfera w pracy'),
        ),
        migrations.AlterField(
            model_name='company',
            name='headquarters_city',
            field=models.CharField(max_length=60, verbose_name='siedziba centrali'),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='nazwa'),
        ),
        migrations.AlterField(
            model_name='company',
            name='overallscore',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='Ocena ogólna'),
        ),
        migrations.AlterField(
            model_name='company',
            name='website',
            field=models.URLField(unique=True, verbose_name='strona www'),
        ),
        migrations.AlterField(
            model_name='company',
            name='worklife',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='Równowaga praca/życie'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='how_got',
            field=models.CharField(choices=[('A', 'Ogłoszenie'), ('B', 'Kontakty profesjonalne'), ('C', 'Head-hunter'), ('D', 'Znajomi-rodzina'), ('E', 'Seks z decydentem'), ('F', 'Inne')], default=None, max_length=1, verbose_name='droga do interview'),
        ),
        migrations.AlterField(
            model_name='review',
            name='worklife',
            field=models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=None, verbose_name='równowaga praca/życie'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-24 13:15
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0014_auto_20170819_2052'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Positions',
            new_name='Job',
        ),
        migrations.RemoveField(
            model_name='position',
            name='city',
        ),
        migrations.RemoveField(
            model_name='position',
            name='years_at_company',
        ),
        migrations.RemoveField(
            model_name='review',
            name='position_ptr',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='position_ptr',
        ),
        migrations.AddField(
            model_name='position',
            name='company_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='position',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='position',
            name='linkedin_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='position',
            name='location',
            field=models.CharField(default='Warszawa', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='position',
            name='start_date_month',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='position',
            name='start_date_year',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='reviews.Company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reviews.Position'),
        ),
        migrations.AddField(
            model_name='salary',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='reviews.Company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salary',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salary',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reviews.Position'),
        ),
        migrations.AlterField(
            model_name='position',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reviews.Company'),
        ),
    ]

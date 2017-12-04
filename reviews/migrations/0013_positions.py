# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-19 18:19
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews', '0012_auto_20170819_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='Positions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=100)),
                ('company_id', models.PositiveIntegerField(blank=True)),
                ('linkedin_id', models.PositiveIntegerField(blank=True)),
                ('location', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('start_date_month', models.PositiveIntegerField()),
                ('start_date_year', models.PositiveIntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

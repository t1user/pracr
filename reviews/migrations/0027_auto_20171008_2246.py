# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-08 20:46
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0026_auto_20171008_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-13 16:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_visit_ip'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='visit',
            options={'verbose_name': 'Wizyta', 'verbose_name_plural': 'Wizyty'},
        ),
        migrations.AddField(
            model_name='visit',
            name='path',
            field=models.CharField(default='', editable=False, max_length=100),
            preserve_default=False,
        ),
    ]

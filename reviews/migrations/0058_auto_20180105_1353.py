# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-05 12:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0057_auto_20180104_1841'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salary',
            old_name='salary_input_gross',
            new_name='salary_gross_input_period',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='base_annual',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='base_monthly',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='bonus_anual',
        ),
        migrations.AddField(
            model_name='salary',
            name='bonus_gross_anual',
            field=models.PositiveIntegerField(blank=True, default=0, editable=False, null=True, verbose_name='premia brutto rocznie'),
        ),
        migrations.AddField(
            model_name='salary',
            name='bonus_gross_input_period',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='premia brutto'),
        ),
        migrations.AddField(
            model_name='salary',
            name='salary_gross_anual',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='pensja brutto rocznie'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='how_got',
            field=models.CharField(choices=[('A', 'Ogłoszenie'), ('B', 'Kontakty zawodowe'), ('C', 'Head-hunter'), ('D', 'Znajomi/rodzina'), ('E', 'Seks z decydentem'), ('F', 'Targi/prezentacje'), ('F', 'Inne')], default=None, max_length=1, verbose_name='droga do interview'),
        ),
    ]

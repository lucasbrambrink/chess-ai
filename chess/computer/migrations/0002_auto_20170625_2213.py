# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-25 22:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('computer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalgame',
            name='file_name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='historicalgame',
            name='hash',
            field=models.CharField(default='', max_length=255),
        ),
    ]

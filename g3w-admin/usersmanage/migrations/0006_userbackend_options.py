# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-08 14:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersmanage', '0005_userbackend'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbackend',
            name='options',
            field=models.TextField(blank=True, null=True, verbose_name='Options'),
        ),
    ]

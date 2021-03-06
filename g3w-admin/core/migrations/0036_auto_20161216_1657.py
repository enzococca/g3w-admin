# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-12-16 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_generalsuitedata'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalsuitedata',
            name='facebook_url',
            field=models.URLField(blank=True, null=True, verbose_name='Facebook link'),
        ),
        migrations.AddField(
            model_name='generalsuitedata',
            name='googleplus_url',
            field=models.URLField(blank=True, null=True, verbose_name='Google+ link'),
        ),
        migrations.AddField(
            model_name='generalsuitedata',
            name='twitter_url',
            field=models.URLField(blank=True, null=True, verbose_name='Twitter link'),
        ),
    ]

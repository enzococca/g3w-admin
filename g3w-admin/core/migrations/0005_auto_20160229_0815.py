# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-29 08:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import sitetree.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('core', '0004_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='G3W2TreeItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Site tree item title. Can contain template variables E.g.: {{ mytitle }}.', max_length=100, verbose_name='Title')),
                ('hint', models.CharField(blank=True, default=b'', help_text='Some additional information about this item that is used as a hint.', max_length=200, verbose_name='Hint')),
                ('url', models.CharField(db_index=True, help_text='Exact URL or URL pattern (see "Additional settings") for this item.', max_length=200, verbose_name='URL')),
                ('urlaspattern', models.BooleanField(db_index=True, default=False, help_text='Whether the given URL should be treated as a pattern.<br /><b>Note:</b> Refer to Django "URL dispatcher" documentation (e.g. "Naming URL patterns" part).', verbose_name='URL as Pattern')),
                ('hidden', models.BooleanField(db_index=True, default=False, help_text='Whether to show this item in navigation.', verbose_name='Hidden')),
                ('alias', sitetree.models.CharFieldNullable(blank=True, db_index=True, help_text='Short name to address site tree item from a template.<br /><b>Reserved aliases:</b> "trunk", "this-children", "this-siblings", "this-ancestor-children", "this-parent-siblings".', max_length=80, null=True, verbose_name='Alias')),
                ('description', models.TextField(blank=True, default=b'', help_text='Additional comments on this item.', verbose_name='Description')),
                ('inmenu', models.BooleanField(db_index=True, default=True, help_text='Whether to show this item in a menu.', verbose_name='Show in menu')),
                ('inbreadcrumbs', models.BooleanField(db_index=True, default=True, help_text='Whether to show this item in a breadcrumb path.', verbose_name='Show in breadcrumb path')),
                ('insitetree', models.BooleanField(db_index=True, default=True, help_text='Whether to show this item in a site tree.', verbose_name='Show in site tree')),
                ('access_loggedin', models.BooleanField(db_index=True, default=False, help_text='Check it to grant access to this item to authenticated users only.', verbose_name='Logged in only')),
                ('access_guest', models.BooleanField(db_index=True, default=False, help_text='Check it to grant access to this item to guests only.', verbose_name='Guests only')),
                ('access_restricted', models.BooleanField(db_index=True, default=False, help_text='Check it to restrict user access to this item, using Django permissions system.', verbose_name='Restrict access to permissions')),
                ('access_perm_type', models.IntegerField(choices=[(1, 'Any'), (2, 'All')], default=1, help_text='<b>Any</b> &mdash; user should have any of chosen permissions. <b>All</b> &mdash; user should have all chosen permissions.', verbose_name='Permissions interpretation')),
                ('sort_order', models.IntegerField(db_index=True, default=0, help_text='Item position among other site tree items under the same parent.', verbose_name='Sort order')),
                ('type_header', models.BooleanField(default=False, verbose_name='Tipo header')),
                ('icon_css_class', models.CharField(blank=True, max_length=50, null=True, verbose_name='Icon css class')),
                ('access_permissions', models.ManyToManyField(blank=True, to='auth.Permission', verbose_name='Permissions granting access')),
                ('parent', models.ForeignKey(blank=True, help_text='Parent site tree item.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='g3w2treeitem_parent', to='core.G3W2TreeItem', verbose_name='Parent')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Site Tree Item',
                'verbose_name_plural': 'Site Tree Items',
            },
        ),
        migrations.RenameModel(
            old_name='Qdjango2Tree',
            new_name='G3W2Tree',
        ),
        migrations.AlterUniqueTogether(
            name='qdjango2treeitem',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='qdjango2treeitem',
            name='access_permissions',
        ),
        migrations.RemoveField(
            model_name='qdjango2treeitem',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='qdjango2treeitem',
            name='tree',
        ),
        migrations.DeleteModel(
            name='Qdjango2TreeItem',
        ),
        migrations.AddField(
            model_name='g3w2treeitem',
            name='tree',
            field=models.ForeignKey(help_text='Site tree this item belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='g3w2treeitem_tree', to='core.G3W2Tree', verbose_name='Site Tree'),
        ),
        migrations.AlterUniqueTogether(
            name='g3w2treeitem',
            unique_together=set([('tree', 'alias')]),
        ),
    ]

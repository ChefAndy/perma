# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-04 17:09
from __future__ import unicode_literals

from django.db import migrations, models


def change_private_reason(apps, schema_editor):
    # Links labeled 'Private by policy' created prior to this deployment
    # were made private because of an implicit `settings.PRIVATE_LINKS_IF_GENERIC_NOARCHIVE = True`.
    # With this release of Perma, we plan to toggle `PRIVATE_LINKS_IF_GENERIC_NOARCHIVE = False`.
    # We want to keep track of which Links were made before and after this change in policy,
    # using this data migration.
    Link = apps.get_model('perma', 'Link')
    private_by_policy = Link.objects.filter(private_reason='policy')
    private_by_policy.update(private_reason='old_policy')


class Migration(migrations.Migration):

    dependencies = [
        ('perma', '0036_auto_20180827_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicallink',
            name='private_reason',
            field=models.CharField(blank=True, choices=[('policy', 'Perma-specific robots.txt or meta tag'), ('old_policy', 'Generic robots.txt or meta tag'), ('user', 'At user direction'), ('takedown', 'At request of content owner'), ('failure', 'Analysis of meta tags failed')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='private_reason',
            field=models.CharField(blank=True, choices=[('policy', 'Perma-specific robots.txt or meta tag'), ('old_policy', 'Generic robots.txt or meta tag'), ('user', 'At user direction'), ('takedown', 'At request of content owner'), ('failure', 'Analysis of meta tags failed')], max_length=10, null=True),
        ),
        migrations.RunPython(change_private_reason, migrations.RunPython.noop, elidable=True),

    ]

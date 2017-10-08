# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0006_auto_20161120_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexed',
            name='ftp_passw',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='indexed',
            name='ftp_user',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='indexed',
            name='host',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='indexed',
            name='init_indexing_path',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='indexed',
            name='id',
            field=models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True),
        ),
    ]

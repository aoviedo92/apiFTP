# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0007_auto_20161121_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indexed',
            name='ftp_user',
        ),
        migrations.RemoveField(
            model_name='indexed',
            name='host',
        ),
        migrations.RemoveField(
            model_name='indexed',
            name='init_indexing_path',
        ),
        migrations.AlterField(
            model_name='indexed',
            name='id',
            field=models.CharField(max_length=255, serialize=False, primary_key=True),
        ),
    ]

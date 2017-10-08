# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0004_auto_20161117_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexed',
            name='dirs_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='indexed',
            name='files_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]

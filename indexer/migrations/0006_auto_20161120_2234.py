# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0005_auto_20161120_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indexed',
            name='dirs_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='indexed',
            name='files_count',
            field=models.IntegerField(default=0),
        ),
    ]

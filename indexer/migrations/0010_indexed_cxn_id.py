# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0009_auto_20161121_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexed',
            name='cxn_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0010_indexed_cxn_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indexed',
            name='cxn_id',
        ),
    ]

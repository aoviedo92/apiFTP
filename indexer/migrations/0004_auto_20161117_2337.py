# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0003_auto_20161117_2321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files',
            name='indexed',
            field=models.ForeignKey(to='indexer.Indexed'),
        ),
    ]

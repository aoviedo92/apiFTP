# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0008_auto_20161121_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indexed',
            name='ftp_passw',
            field=models.CharField(max_length=255, null=True),
        ),
    ]

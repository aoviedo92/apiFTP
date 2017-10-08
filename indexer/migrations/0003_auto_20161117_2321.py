# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0002_auto_20161117_2318'),
    ]

    operations = [
        migrations.AddField(
            model_name='files',
            name='indexed',
            field=models.OneToOneField(to='indexer.Indexed', default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='files',
            name='id',
            field=models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True),
        ),
    ]

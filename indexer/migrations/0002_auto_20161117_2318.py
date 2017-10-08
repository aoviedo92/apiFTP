# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Indexed',
            fields=[
                ('id', models.CharField(primary_key=True, max_length=255, serialize=False)),
            ],
        ),
        migrations.AlterField(
            model_name='files',
            name='id',
            field=models.ForeignKey(primary_key=True, to='indexer.Indexed', related_name='indexed', serialize=False),
        ),
    ]

# Generated by Django 2.2.4 on 2019-08-22 14:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyfy', '0005_auto_20190822_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='acq_date',
            field=models.DateField(blank=True, default=datetime.date.today),
        ),
    ]
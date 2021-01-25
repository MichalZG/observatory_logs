# Generated by Django 3.1.4 on 2021-01-25 23:03

from django.db import migrations, models
import django.utils.timezone
import objects_log.models


class Migration(migrations.Migration):

    dependencies = [
        ('objects_log', '0014_auto_20210123_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='jd_start',
            field=models.DecimalField(blank=True, decimal_places=6, default=1, max_digits=13, verbose_name='JD'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='target',
            name='datetime_end',
            field=models.DateTimeField(default=objects_log.models.auto_end_datetime),
        ),
        migrations.AlterField(
            model_name='target',
            name='datetime_start',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

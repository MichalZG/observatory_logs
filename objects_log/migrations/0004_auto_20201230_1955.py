# Generated by Django 3.1.4 on 2020-12-30 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects_log', '0003_auto_20201230_1953'),
    ]

    operations = [
        migrations.RenameField(
            model_name='target',
            old_name='datatime_start',
            new_name='datetime_start',
        ),
        migrations.AlterField(
            model_name='target',
            name='colorfilter',
            field=models.ManyToManyField(to='objects_log.ColorFilter'),
        ),
    ]

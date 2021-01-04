# Generated by Django 3.1.4 on 2021-01-04 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects_log', '0010_auto_20210103_2359'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='program',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='target',
            options={'ordering': ('datetime_start',)},
        ),
        migrations.RenameField(
            model_name='target',
            old_name='colorfilter',
            new_name='colorfilters',
        ),
        migrations.RenameField(
            model_name='target',
            old_name='tag',
            new_name='tags',
        ),
        migrations.AddField(
            model_name='target',
            name='total_exposure_time',
            field=models.DecimalField(blank=True, decimal_places=3, help_text='Total exposure time in hours', max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='target',
            name='number_of_frames',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

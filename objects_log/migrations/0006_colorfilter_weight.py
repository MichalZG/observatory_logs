# Generated by Django 3.1.4 on 2020-12-31 15:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects_log', '0005_target_number_of_frames'),
    ]

    operations = [
        migrations.AddField(
            model_name='colorfilter',
            name='weight',
            field=models.IntegerField(default=0, help_text='For display sorting purposes', validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)]),
        ),
    ]

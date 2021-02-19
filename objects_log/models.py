from django.db import models
from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from jdcal import gcal2jd
import datetime as dt

class Night(models.Model):
    date = models.DateField(unique=True)
    note = models.TextField(max_length=511, null=True, blank=True)
    tags = models.ManyToManyField('objects_log.Tag', blank=True)

    def __str__(self):
        return self.date.strftime('%d-%m-%Y')
        

def auto_end_datetime():
    return timezone.now() + timezone.timedelta(hours=1)

class Target(models.Model):
    datetime_start = models.DateTimeField(default=timezone.now)
    datetime_end = models.DateTimeField(default=auto_end_datetime)
    jd_start = models.DecimalField(
        max_digits=13, decimal_places=6, verbose_name='JD', blank=True)
    night = models.ForeignKey('objects_log.Night',
        blank=True, on_delete=models.CASCADE)
    observer = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=257)
    ra = models.DecimalField(max_digits=12, decimal_places=10,
        null=True, blank=True, help_text='RA in decimal hours')
    dec = models.DecimalField(max_digits=12, decimal_places=10,
        null=True, blank=True, help_text='DEC in decimal degree')
    note = models.TextField(max_length=511, null=True, blank=True, default='')
    telescope = models.ForeignKey('objects_log.Telescope',
        on_delete=models.PROTECT)
    program = models.ForeignKey('objects_log.Program', null=True, 
        blank=True, on_delete=models.SET_NULL)
    colorfilters = models.ManyToManyField('objects_log.ColorFilter')
    tags = models.ManyToManyField('objects_log.Tag', blank=True)
    total_exposure_time = models.DecimalField(max_digits=7, decimal_places=2,
        null=True, blank=True, help_text='Total exposure time in hours')
    number_of_frames = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ('-datetime_start',)

    def __str__(self):
        return f'{self.name}'

    def get_jd_start(self, dt_value):
        full_days = sum(gcal2jd(
            dt_value.year, dt_value.month, dt_value.day
            ))
        jd = full_days \
            + dt_value.hour / 24 \
            + dt_value.minute / 24 / 60 \
            + dt_value.second / 24 / 60 / 60

        return jd
    
    def get_night(self):
        object_night = (self.datetime_start - dt.timedelta(hours=12)).date()
        night, _ = apps.get_model(
            'objects_log.Night').objects.get_or_create(
                date=object_night,
        )

        return night

    def save(self, *args, **kwargs):
        self.night = self.get_night()
        self.jd_start = self.get_jd_start(self.datetime_start)

        if not self.program:
            last_program = None
            prev_entries = apps.get_model(
                'objects_log.target').objects.filter(
                    name=self.name).order_by("-datetime_start")
            if prev_entries:
                last_program = prev_entries[0].program
            self.program = last_program

        return super().save(*args, **kwargs)


class Observer(models.Model):
    name = models.CharField(max_length=257, unique=True)
    note = models.TextField(max_length=511, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class ColorFilter(models.Model):
    name = models.CharField(max_length=12, unique=True)
    note = models.TextField(max_length=511, null=True, blank=True)
    weight = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ], help_text='For display sorting purposes'
    )

    def __str__(self):
        return f'{self.name}'


class Program(models.Model):
    name = models.CharField(max_length=257, unique=True)
    description = models.TextField(max_length=1023, null=True, blank=True)
    author = models.CharField(max_length=257)
    note = models.TextField(max_length=1023, null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Telescope(models.Model):
    name = models.CharField(max_length=257, unique=True)
    description = models.TextField(max_length=1023, null=True, blank=True)
    note = models.TextField(max_length=1023, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    name = models.CharField(max_length=12, unique=True)
    symbol = models.CharField(
        max_length=12, blank=True,
        null=True, default='9873',
        help_text=('Tag HTML symbol. Example symbols can be found here:\
                    https://www.w3schools.com/charsets/ref_utf_symbols.asp')
    )
    weight = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ], help_text='For display sorting purposes'
    )

    def __str__(self):
        return f'{self.name}'
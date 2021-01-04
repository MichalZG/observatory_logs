from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Target(models.Model):
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    observer = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=257)
    ra = models.DecimalField(max_digits=12, decimal_places=10,
        null=True, blank=True, help_text='RA in decimal hours')
    dec = models.DecimalField(max_digits=12, decimal_places=10,
        null=True, blank=True, help_text='DEC in decimal degree')
    note = models.TextField(max_length=511, null=True, blank=True)
    telescope = models.ForeignKey('objects_log.Telescope', on_delete=models.PROTECT)
    program = models.ForeignKey('objects_log.Program', null=True, 
        blank=True, on_delete=models.SET_NULL)
    colorfilter = models.ManyToManyField('objects_log.ColorFilter')
    tag = models.ManyToManyField('objects_log.Tag', blank=True)
    number_of_frames = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

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
    weight = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ], help_text='For display sorting purposes'
    )

    def __str__(self):
        return f'{self.name}'
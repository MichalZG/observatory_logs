from django.db import models
    

class Target(models.Model):
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    observer = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=257, unique=True)
    ra = models.DecimalField(max_digits=12, decimal_places=10,
        null=True, blank=True, help_text='RA in decimal hours')
    dec = models.DecimalField(max_digits=12, decimal_places=10,
        null=True, blank=True, help_text='DEC in decimal degree')
    note = models.TextField(max_length=511, null=True, blank=True)
    telescope = models.ForeignKey('objects_log.Telescope', on_delete=models.PROTECT)
    program = models.ForeignKey('objects_log.Program', null=True, 
        blank=True, on_delete=models.SET_NULL)
    colorfilter = models.ManyToManyField('objects_log.ColorFilter')
    def __str__(self):
        return f'{self.name}'


class Observer(models.Model):
    name = models.CharField(max_length=257, unique=True)
    note = models.TextField(max_length=511, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class ColorFilter(models.Model):
    name = models.CharField(max_length=5, unique=True)
    note = models.TextField(max_length=511, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class Program(models.Model):
    name = models.CharField(max_length=257, unique=True)
    description = models.TextField(max_length=1023, null=True, blank=True)
    author = models.CharField(max_length=257, unique=True)
    note = models.TextField(max_length=1023, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class Telescope(models.Model):
    name = models.CharField(max_length=257, unique=True)
    description = models.TextField(max_length=1023, null=True, blank=True)
    note = models.TextField(max_length=1023, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'
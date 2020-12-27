from django.db import models
    

class Target(models.Model):
    datatime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    name = models.CharField(max_length=257, unique=True)
    ra = models.DecimalField(max_digits=8, decimal_places=5,
        null=True, blank=True)
    dec = models.DecimalField(max_digits=8, decimal_places=5,
        null=True, blank=True)
    note = models.TextField(max_length=511, null=True, blank=True)
    program = models.ForeignKey('obs_log.Program', null=True, 
        blank=True, on_delete=models.SET_NULL)

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

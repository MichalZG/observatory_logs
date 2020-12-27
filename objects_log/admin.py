from django.contrib import admin
from .models import Target, Observer, ColorFilter, Program

admin.site.register(Target)
admin.site.register(Observer)
admin.site.register(ColorFilter)
admin.site.register(Program)
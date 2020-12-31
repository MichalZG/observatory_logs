from django.contrib import admin
from .models import Target, Observer, ColorFilter, Program, Telescope
from django.conf.locale.en import formats as en_formats
from django.conf.locale.pl import formats as pl_formats

en_formats.DATETIME_FORMAT = "d-m-y H:i:s"
pl_formats.DATETIME_FORMAT = "d-m-y H:i:s"

class TargetAdmin(admin.ModelAdmin):
    
    def colorfilter_display(self, obj):
        return 'R, V, B'

    list_display = ('name', 'datetime_start',
        'colorfilter_display', 'program', 'telescope', 'number_of_frames', 'note')

admin.site.register(Target, TargetAdmin)
admin.site.register(Telescope)
admin.site.register(Observer)
admin.site.register(ColorFilter)
admin.site.register(Program)
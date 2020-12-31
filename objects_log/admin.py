from django.contrib import admin
from .models import Target, Observer, ColorFilter, Program, Telescope
from django.conf.locale.en import formats as en_formats
from django.conf.locale.pl import formats as pl_formats

en_formats.DATETIME_FORMAT = "d-m-y H:i:s"
pl_formats.DATETIME_FORMAT = "d-m-y H:i:s"

class TargetAdmin(admin.ModelAdmin):
    
    def colorfilter_display(self, obj):
        return ', '.join([f.name for f in obj.colorfilter.all()])

    def target_program(self, obj):
        return obj.program

    list_display = ('id', 'name', 'datetime_start',
        'colorfilter_display', 'program', 'telescope', 'number_of_frames', 'note')
    list_display_links = ['id']
    list_editable = ('name', 'program')

    colorfilter_display.short_description = 'Filters'
    target_program.short_description = 'Program'
    # program.empty_value_display = '???'

    class Media:
        css = {"all": ("objects_log/css/style.css",)}

admin.site.register(Target, TargetAdmin)
admin.site.register(Telescope)
admin.site.register(Observer)
admin.site.register(ColorFilter)
admin.site.register(Program)
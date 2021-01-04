from django.contrib import admin
from .models import Target, Observer, ColorFilter, Program, Telescope, Tag
from django.conf.locale.en import formats as en_formats
from django.conf.locale.pl import formats as pl_formats

en_formats.DATETIME_FORMAT = "d-m-y H:i:s"
pl_formats.DATETIME_FORMAT = "d-m-y H:i:s"
NOTE_DISPLAY_LENGHT = 10


class TargetAdmin(admin.ModelAdmin):
    
    def colorfilter_display(self, obj):
        return ', '.join([f.name for f in obj.colorfilter.all()])
    
    def tag_display(self, obj):
        return ', '.join([f.name for f in obj.tag.all()])

    def note_display(self, obj):
        if len(obj.note) > NOTE_DISPLAY_LENGHT:
            return f'{obj.note[:NOTE_DISPLAY_LENGHT]}...'
        return obj.note

    list_display = ('name', 'datetime_start', 'observer',
        'colorfilter_display', 'program', 'telescope', 'number_of_frames', 'note_display', 'tag_display')
    list_editable = ('program',)

    colorfilter_display.short_description = 'Filters'
    tag_display.short_description = 'Tags'
    # program.empty_value_display = '???'

    class Media:
        css = {"all": ("objects_log/css/style.css",)}

admin.site.register(Target, TargetAdmin)
admin.site.register(Tag)
admin.site.register(Telescope)
admin.site.register(Observer)
admin.site.register(ColorFilter)
admin.site.register(Program)
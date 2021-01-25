from django.contrib import admin
from .models import Target, Observer, ColorFilter, Program, Telescope, Tag, Night
from django.db import models
from django.forms import TextInput, Textarea
from django.conf.locale.en import formats as en_formats
from django.conf.locale.pl import formats as pl_formats
from django.utils.html import format_html

en_formats.DATETIME_FORMAT = "d-m-y H:i:s"
pl_formats.DATETIME_FORMAT = "d-m-y H:i:s"
en_formats.DATE_FORMAT = "d-m-Y"
pl_formats.DATE_FORMAT = "d-m-Y"

NOTE_DISPLAY_LENGHT = 10

class TargetInline(admin.TabularInline):
    model = Target
    show_change_link = True

    fields = ('name',)

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False


@admin.register(Night)
class NightAdmin(admin.ModelAdmin):

    def tags_display(self, obj):
        symbols_html = ''.join([f'&#{t.symbol};' for t in obj.tags.all()])
        return format_html(f'<p>{symbols_html}</p>')

    def note_display(self, obj):
        if obj.note and len(obj.note) > NOTE_DISPLAY_LENGHT:
            return f'{obj.note[:NOTE_DISPLAY_LENGHT]}...'
        return obj.note
    
    list_display = ('date', 'tags_display', 'note_display')

    inlines = [
        TargetInline,
    ]

    fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': ('date', ('tags', 'note')),
        }
    ),)


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    # change_list_template = "admin/change_list_filter_sidebar.html"

    class Media:
        css = {
            'all' : ('admin/css/target_side.css',)
        }

    def colorfilters_display(self, obj):
        return ', '.join([f.name for f in obj.colorfilters.all()])
    
    def tags_display(self, obj):
        symbols_html = ''.join([f'&#{t.symbol};' for t in obj.tags.all()])
        return format_html(f'<p>{symbols_html}</p>')

    def note_display(self, obj):
        if len(obj.note) > NOTE_DISPLAY_LENGHT:
            return f'{obj.note[:NOTE_DISPLAY_LENGHT]}...'
        return obj.note

    def total_exposure_time_display(self, obj):
        return obj.total_exposure_time

    list_display = ('name', 'datetime_start', 'jd_start', 'observer',
        'colorfilters_display', 'program', 'telescope', 'total_exposure_time_display',
        'note_display', 'tags_display')

    list_editable = ('program',)

    total_exposure_time_display.short_description = 'Exp [h]'
    note_display.short_description = 'Note'
    colorfilters_display.short_description = 'Filters'
    tags_display.short_description = 'Tags'


    list_filter = ('program', 'tags', 'observer')

    # formfield_overrides = {
    #     models.CharField: {'widget': TextInput(attrs={'size':'10'})},
    #     models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':4})},
    # }

    fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': (('datetime_start', 'datetime_end'), 'name', 'program', 'telescope',
                        'observer', ('colorfilters', 'tags'), 'note')
        }),
    )

    # program.empty_value_display = '???'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    def render_symbol_icon(self, obj):
        return format_html(f'<p>&#{obj.symbol};</p')

    list_display_links = ('id',)
    list_display = ('id', 'name', 'symbol', 'render_symbol_icon')
    list_editable = ('name', 'symbol')

    render_symbol_icon.short_description = 'Symbol icon'


# admin.site.register(Target, TargetAdmin)
# admin.site.register(Tag)
admin.site.register(Telescope)
admin.site.register(Observer)
admin.site.register(ColorFilter)
admin.site.register(Program)
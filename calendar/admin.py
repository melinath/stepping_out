from django.contrib import admin
from django.db.models import DateTimeField
from django import forms
from django.contrib.localflavor.us.forms import USZipCodeField
from django.contrib.admin.widgets import AdminSplitDateTime 
from settings import DEFAULT_ZIP
import models

CALENDAR_FIELDSET = ('Calendars', {
    'fields': ('calendars',),
    'classes': ('collapse-closed',)
})

BASE_EVENT_FIELDS = (
    'name',
    'description',
    'venue',
    ('date', 'time',),
    'length',
)

class BuildingAdminForm(forms.ModelForm):
    class Meta:
        model = models.Building
    
    zipcode = USZipCodeField(initial=DEFAULT_ZIP)

class BuildingAdmin(admin.ModelAdmin):
    form = BuildingAdminForm
    list_display = ('name_or_address', 'city', 'state', 'zipcode',)
    ordering = ('state', 'city',)
    list_filter = ('city', 'state', 'zipcode',)
    
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'building', 'display')
    list_editable = ('display',)

class EventAdminForm(forms.ModelForm):
        
    def clean_length(self):
        length = self.cleaned_data['length']
        
        if length <= 0:
            raise forms.ValidationError(
                'Length must be positive'
            )
            
        return length

class MeetingAdminForm(EventAdminForm):
    class Meta:
        model = models.Meeting

class LessonAdminForm(EventAdminForm):
    class Meta:
        model = models.Lesson

class DanceAdminForm(forms.ModelForm):
    class Meta:
        model = models.Dance
    """    
    def clean_length(self):
        length = self.cleaned_data['length']
        
        if length != -1 and length <= 0:
            raise forms.ValidationError(
                'Length can only be positive or -1 (indefinite)'
            )
            
        return length
    """

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'description',)
    ordering = ('-date', '-time',)
    date_hierarchy = 'date'
        
class MeetingAdmin(EventAdmin):
    form = MeetingAdminForm

class DanceAdmin(EventAdmin):
    form = DanceAdminForm
    raw_id_fields = ("lesson", "workshop",)
    filter_horizontal = ['calendars']
    list_display = (
        'name',
        'venue',
        'date',
        'time',
        'length',
        'external_calendar',
    )
    
    fieldsets = (
        ('Basic Info', {
            'fields': BASE_EVENT_FIELDS + ('lesson',)
        }),
        CALENDAR_FIELDSET,
        ('Workshop', {
            'description': """Fill out this field with the workshop this lesson
            is related to.""",
            'fields': ('workshop',),
            'classes': ('collapse-closed',)
        })
    )
        
class LessonAdmin(EventAdmin):
    form = LessonAdminForm
    raw_id_fields = ("workshop",)
    filter_horizontal = ['teachers', 'calendars']
    list_display = (
        'name',
        'venue',
        'date',
        'time',
        'length',
        'difficulty',
        'external_calendar',
    )
    fieldsets = (
        ('Basic Info', {
            'fields': BASE_EVENT_FIELDS
        }),
        ('Additional Class Info', {
            'fields': ('difficulty', 'teachers',),
            'classes': ('collapse-open',)
        }),
        CALENDAR_FIELDSET,
        ('Workshop', {
            'description': """Fill out this field with the workshop this lesson
            is related to.""",
            'fields': ('workshop',),
            'classes': ('collapse-open',)
        })
    )

class WorkshopAdmin(EventAdmin):
    list_display = ('name', 'date', 'description',)
    ordering = ('-date',)
    filter_horizontal = ['calendars']
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'date', 'end_date', 'website')
        }),
        ('Location', {
            'fields': ('city', 'state', 'zipcode')
        }),
        CALENDAR_FIELDSET,
    )
    
class LocalCalendarAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
class ExternalCalendarAdmin(admin.ModelAdmin):
    fields = ('name', 'url',)
    list_display = ('name', 'url', 'last_checked',)

class DeadlineAdmin(admin.ModelAdmin):
    filter_horizontal = ['calendars']
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'date', 'time')
        }),
        CALENDAR_FIELDSET,
    )

admin.site.register(models.Deadline, DeadlineAdmin)
admin.site.register(models.Building, BuildingAdmin)
admin.site.register(models.Venue, VenueAdmin)
admin.site.register(models.Workshop, WorkshopAdmin)
admin.site.register(models.Dance, DanceAdmin)
admin.site.register(models.Lesson, LessonAdmin)
admin.site.register(models.Meeting, MeetingAdmin)
admin.site.register(models.LocalCalendar, LocalCalendarAdmin)
admin.site.register(models.ExternalCalendar, ExternalCalendarAdmin)
admin.site.register(models.Ride)
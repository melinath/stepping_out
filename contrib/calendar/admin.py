from django import forms
from django.contrib import admin
from stepping_out.contrib.calendar.models import Calendar, Ride


class CalendarAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields': ('name', 'calendar_id', 'events',)
		}),
		('Advanced', {
			'fields': ('sync_with_url',),
			'classes': ('closed', 'collapse-closed', 'collapse')
		}),
	)
	filter_horizontal = ['events']


class RideAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields': ('event', 'seats', 'driver', 'passengers'),
		}),
		(None, {
			'fields': ('meeting_time', 'meeting_place'),
		}),
	)
	filter_horizontal = ['passengers']

admin.site.register(Ride, RideAdmin)
admin.site.register(Calendar, CalendarAdmin)
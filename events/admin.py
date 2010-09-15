from django.contrib import admin
from stepping_out.events.models import *


class BuildingAdmin(admin.ModelAdmin):
	pass


class VenueAdmin(admin.ModelAdmin):
	pass


class EventAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields': ('title', 'description', 'venue')
		}),
		('Times', {
			'fields': ('start_date', 'start_time', 'end_date', 'end_time')
		}),
		('Advanced', {
			'fields': ('parent_event',)
		})
	)


class AgendaItemInline(admin.TabularInline):
	model = AgendaItem


class AgendaAdmin(admin.ModelAdmin):
	inlines = [
		AgendaItemInline
	]


class MinutesEntryInline(admin.TabularInline):
	model = MinutesEntry


class MinutesAdmin(admin.ModelAdmin):
	inlines = [
		MinutesEntryInline
	]


admin.site.register(Building, BuildingAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Agenda, AgendaAdmin)
admin.site.register(Minutes, MinutesAdmin)
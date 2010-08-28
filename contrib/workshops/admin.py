from django.contrib import admin
from stepping_out.contrib.workshops.models import Workshop, WorkshopEvent, WorkshopTrack
from stepping_out.pricing.admin import PricePackageInline


class WorkshopEventInline(admin.StackedInline):
	model = WorkshopEvent
	extra = 0


class WorkshopTrackInline(admin.StackedInline):
	model = WorkshopTrack
	extra = 0


class WorkshopTrackAdmin(admin.ModelAdmin):
	inlines = [WorkshopEventInline]


class WorkshopAdmin(admin.ModelAdmin):
	inlines = [
		WorkshopTrackInline,
		WorkshopEventInline,
		PricePackageInline
	]


admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(WorkshopTrack, WorkshopTrackAdmin)
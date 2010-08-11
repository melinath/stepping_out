from django.contrib import admin
from stepping_out.contrib.workshops.models import Workshop, WorkshopEvent
#from stepping_out.pricing.admin import PricePackageInline


class WorkshopEventInline(admin.StackedInline):
	model = WorkshopEvent


class WorkshopAdmin(admin.ModelAdmin):
	inlines = [
		WorkshopEventInline,
		#PricePackageInline
	]


admin.site.register(Workshop, WorkshopAdmin)
from django.contrib import admin
from stepping_out.contrib.workshops.models import Workshop, WorkshopEvent, WorkshopTrack, HousingRequest, HousingOffer, Registration
from stepping_out.pricing.admin import PricePackageInline


COLLAPSE_CLOSED_CLASSES = ('collapse-closed', 'collapse', 'closed')


class HousingRequestAdmin(admin.ModelAdmin):
	pass


class HousingRequestInline(admin.StackedInline):
	model = HousingRequest
	classes = COLLAPSE_CLOSED_CLASSES


class HousingOfferAdmin(admin.ModelAdmin):
	pass


class HousingOfferInline(admin.StackedInline):
	model = HousingOffer
	classes = COLLAPSE_CLOSED_CLASSES


class RegistrationAdmin(admin.ModelAdmin):
	inlines = [HousingOfferInline, HousingRequestInline]


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


admin.site.register(HousingRequest, HousingRequestAdmin)
admin.site.register(HousingOffer, HousingOfferAdmin)
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(WorkshopTrack, WorkshopTrackAdmin)
admin.site.register(Registration, RegistrationAdmin)
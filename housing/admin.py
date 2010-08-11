from django.contrib import admin
from stepping_out.housing.models import OfferedHousing, RequestedHousing, HousingCoordinator


COLLAPSE_CLOSED_CLASSES = ('collapse-closed', 'collapse', 'closed')


class OfferedHousingInline(admin.StackedInline):
	model = OfferedHousing
	extra = 1
	classes = COLLAPSE_CLOSED_CLASSES


class RequestedHousingInline(admin.StackedInline):
	model = RequestedHousing
	extra = 1
	classes = COLLAPSE_CLOSED_CLASSES


class HousingCoordinatorAdmin(admin.ModelAdmin):
	inlines = [OfferedHousingInline, RequestedHousingInline]


admin.site.register(HousingCoordinator, HousingCoordinatorAdmin)
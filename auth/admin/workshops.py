from django.contrib import admin
from stepping_out.auth.models.workshops import *


__all__ = (
	'WorkshopProfileInline',
	'HousingProfileInline',
	'HousingPreferencesProfileInline'
)
COLLAPSE_CLOSED_CLASSES = ('collapse', 'collapse-closed', 'closed',)


class WorkshopProfileInline(admin.TabularInline):
	model = WorkshopProfile
	verbose_name_plural = 'Workshop profile'
	classes = COLLAPSE_CLOSED_CLASSES


class HousingProfileInline(admin.TabularInline):
	model = HousingProfile
	verbose_name_plural = 'Housing profile'
	classes = COLLAPSE_CLOSED_CLASSES


class HousingPreferencesProfileInline(admin.TabularInline):
	model = HousingPreferencesProfile
	verbose_name_plural = 'Housing preferences profile'
	classes = COLLAPSE_CLOSED_CLASSES
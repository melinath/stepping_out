from django.contrib import admin
from models import WorkshopProfile, HousingProfile, HousingPreferencesProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

"""
Teachers and bands should be able to edit their own data - i.e. instructor
bios etc. - but not via the admin interface.
"""

class WorkshopProfileInline(admin.TabularInline):
    model = WorkshopProfile
    
class HousingProfileInline(admin.TabularInline):
    model = HousingProfile
    
class HousingPreferencesProfileInline(admin.TabularInline):
    model = HousingPreferencesProfile

    
USER_INLINES = [
    WorkshopProfileInline,
    HousingProfileInline,
    HousingPreferencesProfileInline,
]
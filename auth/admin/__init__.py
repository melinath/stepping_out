"""
Essentially, pull everything together here and define the actual User admin.
"""


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from stepping_out.auth.admin.auth import OfficerPositionInline
from stepping_out.auth.admin.mail import UserEmailInline
from stepping_out.auth.admin.workshops import WorkshopProfileInline, HousingProfileInline, HousingPreferencesProfileInline
from stepping_out.auth.widgets import SelectOther, AdminEmailInputWidget


USER_INLINES = [
	UserEmailInline,
	OfficerPositionInline,
	WorkshopProfileInline,
	HousingProfileInline,
	HousingPreferencesProfileInline
]
COLLAPSE_CLOSED_CLASSES = ('collapse', 'collapse-closed', 'closed',)


class SteppingOutUserAdmin(UserAdmin):
	inlines = USER_INLINES + UserAdmin.inlines
	fieldsets = (
		(None, {
			'fields': ('username', 'password')
		}),
		('Permissions', {
			'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions'),
			'classes': COLLAPSE_CLOSED_CLASSES
		}),
		('Important dates', {
			'fields': ('last_login', 'date_joined'),
			'classes': COLLAPSE_CLOSED_CLASSES
		}),
		('Groups', {
			'fields': ('groups',),
			'classes': COLLAPSE_CLOSED_CLASSES
		}),
		('Personal Information', {
			'fields': ('first_name', 'last_name', 'phone_number', 'email')
		}),
	)
	filter_horizontal = ('groups',)
	#The value for email, when the model is saved, should be added to the useremails
	#if it doesn't already exist.
	# so on save, expect to process a string.
	
	def get_form(self, request, obj=None, **kwargs):
		form = super(SteppingOutUserAdmin, self).get_form(request, obj, **kwargs)
		
		if obj:
			CHOICES = [(email.email, email.email) for email in obj.emails.all()]
		else:
			CHOICES = ()
		
		form.base_fields['email'].widget = SelectOther(other=AdminEmailInputWidget, choices=CHOICES)
		return form
	
	def save_model(self, request, obj, form, change):
		primary_email = obj.emails.get_or_create(email=obj.email)
		super(SteppingOutUserAdmin, self).save_model(request, obj, form, change)

from django.utils.translation import ugettext_lazy as _
User._meta.get_field('email').verbose_name = _('primary email')


admin.site.unregister(User)
admin.site.register(User, SteppingOutUserAdmin)
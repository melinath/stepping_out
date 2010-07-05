"""
Essentially, pull everything together here and define the actual User admin.
"""


from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from stepping_out.auth.admin.auth import OfficerPositionInline
from stepping_out.auth.admin.mail import UserEmailInline
from stepping_out.auth.admin.workshops import WorkshopProfileInline, HousingProfileInline, HousingPreferencesProfileInline
from stepping_out.auth.widgets import SelectOther, AdminEmailInputWidget
from stepping_out.auth.validators import UserEmailValidator
from django.utils.translation import ugettext_lazy as _
from django.core.validators import validate_email


USER_INLINES = [
	UserEmailInline,
	OfficerPositionInline,
	WorkshopProfileInline,
	HousingProfileInline,
	HousingPreferencesProfileInline
]
COLLAPSE_CLOSED_CLASSES = ('collapse', 'collapse-closed', 'closed',)


class SteppingOutUserAdminForm(UserChangeForm):
	def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
				initial=None, error_class=forms.util.ErrorList, label_suffix=':',
				empty_permitted=False, instance=None):
		if instance:
			CHOICES = [(email.email, email.email) for email in instance.emails.all()]
		else:
			CHOICES = ()
		
		self.base_fields['email'] = forms.CharField(
			label='Primary email',
			widget=SelectOther(other=AdminEmailInputWidget, choices=CHOICES),
			required=False,
			validators = [validate_email, UserEmailValidator(instance=instance)]
		) 
		super(SteppingOutUserAdminForm, self).__init__(
			data, files, auto_id, prefix, initial, error_class, label_suffix,
			empty_permitted, instance
		)
	
	def save(self, commit=True):
		instance = super(SteppingOutUserAdminForm, self).save(commit)
		#if commit: - should this be deferred somehow? The admin uses commit=False
		email = instance.emails.get_or_create(email=instance.email)
		return instance


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
	form = SteppingOutUserAdminForm


User._meta.get_field('email')._unique = True


admin.site.unregister(User)
admin.site.register(User, SteppingOutUserAdmin)
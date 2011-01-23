from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django import forms
from stepping_out.auth.models import *
from stepping_out.auth.widgets import SelectOther, AdminEmailInputWidget
from stepping_out.mail.admin import UserEmailInline


COLLAPSE_CLOSED_CLASSES = ('collapse', 'collapse-closed', 'closed',)


class OfficerForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(OfficerForm, self).__init__(*args, **kwargs)
		self.fields['start'].required = False
		self.fields['end'].required = False
	
	class Meta:
		model = Officer


class OfficerAdmin(admin.ModelAdmin):
	form = OfficerForm
	raw_id_fields = ('position', 'user', 'term')


class OfficerPositionAdmin(admin.ModelAdmin):
	list_editable = ['order']
	list_display = ['name', 'order']
	prepopulated_fields = {'slug': ('name',)}


class TermAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'start', 'end']


class SteppingOutUserAdminForm(UserChangeForm):
	def __init__(self, *args, **kwargs):
		super(SteppingOutUserAdminForm, self).__init__(*args, **kwargs)
		
		if self.instance.pk:
			CHOICES = [(email.email, email.email) for email in self.instance.emails.all()]
		else:
			CHOICES = ()
		
		self.fields['email'] = forms.CharField(
			label='Primary email',
			widget=SelectOther(other=AdminEmailInputWidget, choices=CHOICES),
			required=False,
			validators = [validate_email]
		)


class SteppingOutUserAdmin(UserAdmin):
	inlines = [UserEmailInline,] + UserAdmin.inlines
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
admin.site.register(OfficerPosition, OfficerPositionAdmin)
admin.site.register(Officer, OfficerAdmin)
admin.site.register(Term, TermAdmin)
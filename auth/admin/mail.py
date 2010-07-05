from django.contrib import admin
from stepping_out.auth.models.mail import *
from django.forms.models import BaseInlineFormSet


class UserEmailInline(admin.TabularInline):
	model = UserEmail
	extra = 1
	verbose_name = 'email address'
	verbose_name_plural = 'email addresses'
from django.contrib.auth.models import User
from stepping_out.modules import *
from stepping_out.auth.models import UserEmail
from stepping_out.auth.forms import PrimaryUserEmailFormSet


class UserProxy(ModelProxy):
	model = User


class UserEmailProxy(ModelProxy):
	model = UserEmail
	related_field_name = 'user'


class UserSettingsModule(Module):
	verbose_name = "Account preferences"
	slug = "preferences"
	help_text = "Here you can set all sorts of exciting profile information!"
	first_name = ProxyField(UserProxy)
	last_name = ProxyField(UserProxy)
	emails = InlineField(UserEmailProxy, fields=['email'], extra=1,
		formset=PrimaryUserEmailFormSet)


class UserSettingsAdmin(ModuleAdmin):
	order = 0


site.register(UserSettingsModule, UserSettingsAdmin)
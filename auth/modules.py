from django.contrib.auth.models import User
from stepping_out.modules import ModelProxy, Module, ProxyField, site, ModuleAdmin
from stepping_out.auth.models import UserEmail


class UserProxy(ModelProxy):
	model = User


class UserEmailProxy(ModelProxy):
	model = UserEmail
	#FIXME: actually get this kind of thing working.


class UserSettingsModule(Module):
	verbose_name = "Account preferences"
	slug = "preferences"
	help_text = "Here you can set all sorts of exciting profile information!"
	first_name = ProxyField(UserProxy)
	last_name = ProxyField(UserProxy)


class UserSettingsAdmin(ModuleAdmin):
	order = 0


site.register(UserSettingsModule, UserSettingsAdmin)
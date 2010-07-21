from stepping_out.modules import Module, InlineModule, ModuleInlineModel, Section, site
from stepping_out.modules.defaults import UserModel
from stepping_out.auth.models import UserEmail


class ProfileModule(Module):
	models = (
		UserModel(['first_name', 'last_name',]),
	)
	fieldsets = (
		(None, {
			'fields': ['first_name', 'last_name']
		}),
	)


class RideModule(Module):
	models = (
		UserModel(['phone_number']),
	)


class UserEmailModel(ModuleInlineModel):
	model = UserEmail


class EmailModule(InlineModule):
	models = (
		UserEmailModel(['email']),
		)


#class WorkshopModule(Module):
#	models = (
#		((WorkshopProfile, 'user'), ['student', 'zip']),
#	)


#class PasswdModule(Module):
#	models = (
#		(User, [('password', 'pwd')]),
#	)



class PreferencesSection(Section):
	title = "Account Preferences"
	slug = "preferences"
	help_text = "Here you can set all sorts of exciting profile information!"
	modules = [
		ProfileModule,
		RideModule,
		EmailModule,
		#WorkshopModule,
		#PasswdModule
	]


site.register(PreferencesSection)
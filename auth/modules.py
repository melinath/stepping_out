from stepping_out.modules import Module, Section, site
from stepping_out.modules.defaults import UserModel


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
		#WorkshopModule,
		#PasswdModule
	]


site.register(PreferencesSection)
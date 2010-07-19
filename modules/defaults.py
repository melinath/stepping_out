from stepping_out.modules.modules import ModuleModel
from stepping_out.modules.sections import Section
from stepping_out.modules.sites import site
from django.contrib.auth.models import User


class UserModel(ModuleModel):
	model = User
	
	def _get_for_user(self, user):
		return user


class HomeSection(Section):
	title = 'Home'
	slug = 'home'
	template = 'stepping_out/modules/home.html'
	modules = []


site.register(HomeSection)
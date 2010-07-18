from stepping_out.modules import ModuleModel, Section, site
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
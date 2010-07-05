"""
A class of tracked user lists to be selected in the admin interface. User List
plugins must have a get_list method (accessed by the list property) which
returns a list of User objects.
TODO: Use signals to handle adding/dropping of userlist models for officer positions.
"""


from stepping_out.auth.models import OfficerPosition
from django.template.defaultfilters import slugify


class UserListPluginMount(type):
	def __init__(cls, name, bases, attrs):
		if not hasattr(cls, 'plugins'):
			cls.plugins = {}
		else:
			cls.plugins[slugify(name)] = cls


class UserListPlugin(object):
	"""
	Plugins extending this class are expected to accept one arg on init, and
	to have a get_list(self) method which returns a list of User objects.
	"""
	__metaclass__ = UserListPluginMount
	
	def __init__(self, arg):
		if arg == '':
			self.arg = None
		else:
			self.arg = arg
	
	def get_list(self):
		raise NotImplementedError


class CurrentOfficers(UserListPlugin):
	"""
	The arg in this case is the id of the officer position.
	"""
	def get_list(self):
		if self.arg:
			userlist = OfficerPosition.objects.get(id=self.arg).current_users
		else:
			userlist = []
			for position in OfficerPosition.objects.all():
				userlist.extend(position.current_users)
		
		return userlist
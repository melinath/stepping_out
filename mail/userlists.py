"""
A class of tracked user lists to be selected in the admin interface. User List
plugins must have a get_list method (accessed by the list property) which
returns a list of User objects.
"""


from stepping_out.auth.models import OfficerPosition
from django.template.defaultfilters import slugify
from django.db.models import signals


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


def add_officer_userlist(instance, created, **kwargs):
	from stepping_out.mail.models import UserList
	if created:
		UserList.objects.get_or_create(
			name = "Current Officers (%s)" % instance.name,
			json_value = str(instance.id),
			plugin = 'currentofficers'
		)

def del_officer_userlist(instance, **kwargs):
	from stepping_out.mail.models import UserList
	try:
		obj = UserList.objects.get(plugin='currentofficers', json_value=str(instance.id))
	except UserList.DoesNotExist:
		pass
	else:
		obj.delete()

signals.post_save.connect(add_officer_userlist, sender=OfficerPosition)
signals.post_delete.connect(del_officer_userlist, sender=OfficerPosition)
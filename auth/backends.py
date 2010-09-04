from django.contrib.auth.models import User, Permission
from django.contrib.auth.backends import ModelBackend


class SteppingOutBackend(ModelBackend):
	"""Handles authentication with user emails and permissions for officers."""
	def authenticate(self, username=None, password=None):
		"""username is passed as a kwarg, but we're actually checking if it's an email address."""
		try:
			user = User.objects.get(emails__email=username)
			if user.check_password(password):
				return user
		except User.DoesNotExist:
			return None
	
	def get_officer_permissions(self, user_obj):
		if not hasattr(user_obj, '_officer_perm_cache'):
			perms = Permission.objects.filter(officerposition__users=user_obj
				).values_list('content_type__app_label', 'codename'
				).order_by()
			user_obj._officer_perm_cache = set(["%s.%s" % (ct, name) for ct, name in perms])
		return user_obj._group_perm_cache
	
	def get_all_permissions(self, user_obj):
		return self.get_officer_permissions(user_obj)
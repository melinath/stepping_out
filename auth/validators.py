from django.core.exceptions import ValidationError
from stepping_out.auth.models import UserEmail
from django.utils.translation import ugettext_lazy as _


class UserEmailValidator(object):
	message = _('Another user already has that email.')
	code = 'invalid'
	
	def __init__(self, instance=None, message=None, code=None):
		if message is not None:
			self.message = message
		
		if code is not None:
			self.code = code
		
		self.instance = instance
	
	def __call__(self, value):
		try:
			UserEmail.objects.exclude(user=self.instance).get(email=value)
		except UserEmail.DoesNotExist:
			pass
		else:
			raise ValidationError(self.message)#, code=self.code)
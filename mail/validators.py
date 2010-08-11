from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, email_re
from django.utils.translation import ugettext_lazy as _
import re


pattern = email_re.pattern.split('@')


class EmailNameValidator(RegexValidator):
	regex = re.compile(pattern[0] + '$', re.IGNORECASE)


class EmailDomainValidator(RegexValidator):
	regex = re.compile('^' + pattern[1], re.IGNORECASE)


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
		from stepping_out.mail.models import UserEmail
		try:
			UserEmail.objects.exclude(user=self.instance).get(email=value)
		except UserEmail.DoesNotExist:
			pass
		else:
			raise ValidationError(self.message)#, code=self.code)
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError


__all__ = ('UserEmail',)


class UserEmail(models.Model):
	email = models.EmailField(unique=True)
	user = models.ForeignKey(User, related_name='emails')
	
	def delete(self):
		user = self.user
		super(UserEmail, self).delete()
		if user.email == self.email:
			user.email = user.emails.all()[0].email
	
	def __unicode__(self):
		return self.email
	
	class Meta:
		app_label = 'stepping_out'


def validate_user_emails(instance, **kwargs):
	try:
		UserEmail.objects.exclude(user=instance).get(email=instance.email)
	except UserEmail.DoesNotExist:
		pass
	else:
		raise ValidationError('A user with that email already exists.')


def sync_user_emails(instance, created, **kwargs):
	instance.emails.get_or_create(email=instance.email)


models.signals.pre_save.connect(validate_user_emails, sender=User)
models.signals.post_save.connect(sync_user_emails, sender=User)
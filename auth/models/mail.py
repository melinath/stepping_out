from django.contrib.auth.models import User
from django.db import models


__all__ = ('UserEmail',)


class UserEmail(models.Model):
	email = models.EmailField(unique=True)
	user = models.ForeignKey(User, related_name='emails')
	
	def __unicode__(self):
		return self.email
	
	class Meta:
		app_label = 'stepping_out'
from django.db import models
from django.db.models import PositiveIntegerField
from django.contrib.auth.models import User, Permission
from django.contrib.localflavor.us.models import PhoneNumberField
from datetime import datetime


__all__ = (
	'Term',
	'OfficerUserMetaInfo',
	'OfficerPosition'
)


PhoneNumberField(blank=True).contribute_to_class(User, 'phone_number')


class TermManager(models.Manager):
	def get_current(self):
		return self.exclude(start__gt=datetime.now).exclude(end__lt=datetime.now)


class Term(models.Model):
	start = models.DateField()
	end = models.DateField()
	name = models.CharField(max_length=30, blank = True)
	objects = TermManager()
	
	def __unicode__(self):
		if(self.name):
			return self.name
			
		return "%s -> %s" % (self.start,self.end)
	
	class Meta:
		app_label = 'stepping_out' 


class OfficerUserMetaInfo(models.Model):
	officer_position = models.ForeignKey('OfficerPosition')
	user = models.ForeignKey(User)
	terms = models.ManyToManyField(Term)
	
	class Meta:
		verbose_name = 'Officer/User Meta Info'
		verbose_name_plural = 'Officer/User Meta Info'
		app_label = 'stepping_out'
		
	def __unicode__(self):
		return '%s :: %s' % (self.user.get_full_name(), self.officer_position)
		

class OfficerPosition(models.Model):
	"""
	Officer Positions are non-generic groupings that connect users into the
	permissions framework - based on meta information such as terms of office.
	
	Conveniently, these positions can also be used to automatically generate a
	list of current officers, through the extended manager.	  
	"""
	name = models.CharField(max_length=50)
	permissions = models.ManyToManyField(Permission, blank=True, null=True)
	order = models.IntegerField()
	users = models.ManyToManyField(User, through='OfficerUserMetaInfo')
	
	def __unicode__(self):
		return self.name
	
	def users_for_terms(self, termlist):
		return self.users.filter(officerusermetainfo__terms__in=termlist)
	
	@property
	def current_users(self):
		return self.users_for_terms(Term.objects.get_current())
	
	class Meta:
		app_label = 'stepping_out'
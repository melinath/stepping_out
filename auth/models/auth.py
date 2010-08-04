"""
Models which are strictly auth-related.
"""


from django.db import models
from django.db.models import PositiveIntegerField
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.localflavor.us.models import PhoneNumberField
from datetime import datetime
import os, base64


__all__ = (
	'Term',
	'OfficerUserMetaInfo',
	'OfficerPosition',
	'PendConfirmation',
	'PendConfirmationData'
)


ADD_NEW = 'new'
DELETE = 'delete'
ACTION_CHOICES = (
	(ADD_NEW, 'New'),
	(DELETE, 'Delete')
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


def randstr(leng):
	"""Alternative:
	http://stackoverflow.com/questions/785058/random-strings-in-python-2-6-is-this-ok"""
	return base64.urlsafe_b64encode(str(os.urandom(leng)))[:leng]


class PendConfirmation(models.Model):
	"""This model contains all information necessary for saving information
	pending confirmation via an emailed link. It also handles the sending of
	the information, the generation of the confirmation key, and the...
	anything else? Currently only supports pending of text (and integer?) data.
	"""
	code = models.CharField(max_length=75, unique=True)
	content_type = models.ForeignKey(ContentType)
	object_id = PositiveIntegerField(blank=True, null=True)
	item = GenericForeignKey()
	action = models.CharField(max_length=10, choices=ACTION_CHOICES)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		action = dict(self._meta.get_field('action').choices)[self.action]
		return "%s %s" % (action, self.item or self.content_type)
	
	def save(self, commit=True):
		if not self.code:
			while True:
				self.code = randstr(50)
				try:
					PendConfirmation.objects.get(code=self.code)
				except PendConfirmation.DoesNotExist:
					break
		return super(PendConfirmation, self).save(commit)
	
	def confirm(self):
		if self.object_id is not None:
			instance = self.content_type.get_object_for_this_type(pk=self.object_id)
		else:
			instance = self.content_type.model_class()()
		
		for kv in self.kv_pairs.all():
			setattr(instance, kv.key, kv.value)
		
		if self.action == ADD_NEW:
			# FIXME: Validate the model I've created!
			instance.save()
		elif self.action == DELETE:
			instance.delete()
		self.delete()
		return instance
	
	class Meta:
		app_label = 'stepping_out'


class PendConfirmationData(models.Model):
	confirmation = models.ForeignKey(PendConfirmation, related_name='kv_pairs')
	key = models.CharField(max_length=255)
	value = models.TextField()
	
	def __unicode__(self):
		return u"%s: %s" % (self.key, self.value)
	
	class Meta:
		app_label = 'stepping_out'
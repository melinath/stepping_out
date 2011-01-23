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
	"""Describes a term of office."""
	start = models.DateField()
	end = models.DateField()
	name = models.CharField(max_length=30, blank=True)
	objects = TermManager()
	positions = models.ManyToManyField('OfficerPosition', related_name="terms", through='OfficerUserTermMetaInfo')

	def __unicode__(self):
		if(self.name):
			return self.name

		return "%s -> %s" % (self.start,self.end)

	class Meta:
		app_label = 'stepping_out'


class OfficerUserTermMetaInfo(models.Model):
	officer_position = models.ForeignKey('OfficerPosition')
	user = models.ForeignKey(User)
	term = models.ForeignKey(Term)
	
	start = models.DateField()
	end = models.DateField()
	
	def save(self, *args, **kwargs):
		if self.start is None:
			self.start = self.term.start
		if self.end is None:
			self.end = self.term.end
		super(OfficerUserTermMetaInfo, self).save(*args, **kwargs)

	class Meta:
		verbose_name = 'Officer/User Meta Info'
		verbose_name_plural = 'Officer/User Meta Info'
		app_label = 'stepping_out'

	def __unicode__(self):
		return '%s :: %s' % (self.user.get_full_name(), self.officer_position)


class OfficerPositionManager(models.Manager):
	def get_user_positions(self, user, termlist):
		return self.filter(users=user, users__officerusermetainfo__terms__in=termlist)

	def get_user_current_positions(self, user):
		return self.get_user_positions(user, Term.objects.get_current())


class OfficerPosition(models.Model):
	"""
	Officer Positions are non-generic groupings that connect users into the
	permissions framework - based on meta information such as terms of office.

	Conveniently, these positions can also be used to automatically generate a
	list of current officers, through the extended manager.
	"""
	#TODO: Update the admin.
	CATEGORY_CHOICES = (
		('o', 'Officer'),
		('i', 'Instructor'),
	)
	objects = OfficerPositionManager()
	
	name = models.CharField(max_length=50)
	slug = models.SlugField(max_length=50)
	description = models.TextField(help_text="A description of the officer's roles and responsibilities.")
	
	permissions = models.ManyToManyField(Permission, blank=True, null=True)
	order = models.IntegerField()
	category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
	users = models.ManyToManyField(User, related_name="officer_positions", through=OfficerUserTermMetaInfo)

	def __unicode__(self):
		return self.name

	def users_for_terms(self, termlist):
		return self.users.filter(officerusermetainfo__terms__in=termlist)

	@property
	def current_users(self):
		return self.users_for_terms(Term.objects.get_current())

	class Meta:
		app_label = 'stepping_out'
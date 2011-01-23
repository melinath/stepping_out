#encoding: utf-8
from django.db import models
from django.db.models import PositiveIntegerField
from django.contrib.auth.models import User, Permission
from django.contrib.localflavor.us.models import PhoneNumberField
import datetime


__all__ = (
	'Term',
	'Officer',
	'OfficerPosition'
)


PhoneNumberField(blank=True).contribute_to_class(User, 'phone_number')


class TermManager(models.Manager):
	def for_date(self, date):
		self.exclude(start__gte=date).exclude(end__lte=date)
	
	def current(self):
		return self.for_date(datetime.date.today())


class Term(models.Model):
	"""Describes a term of office."""
	objects = TermManager()
	
	start = models.DateField()
	end = models.DateField()
	name = models.CharField(max_length=30, blank=True)
	positions = models.ManyToManyField('OfficerPosition', related_name="terms", through='Officer')
	
	def is_current(self):
		return self.start <= datetime.date.today() <= self.end
	
	def __unicode__(self):
		if self.name:
			return self.name

		return "%s – %s" % (self.start,self.end)

	class Meta:
		app_label = 'stepping_out'


class OfficerManager(models.Manager):
	def for_date(self, date):
		return self.exclude(end__lt=date).exclude(start__gt=date)
	
	def current(self):
		return self.for_date(datetime.date.today())


class Officer(models.Model):
	objects = OfficerManager()
	
	position = models.ForeignKey('OfficerPosition')
	user = models.ForeignKey(User, related_name='officers')
	term = models.ForeignKey(Term, related_name='officers')
	
	start = models.DateField()
	end = models.DateField()

	def __unicode__(self):
		return '%s :: %s' % (self.user.get_full_name(), self.position)
	
	def clean(self):
		if self.start and self.end:
			if self.start < self.term.start or self.end > self.term.end:
				raise ValidationError("An officer position cannot be held beyond its term.")
			
			if self.end <= self.start:
				raise ValidationError("An officer position can't end before it starts.")
	
	def save(self, *args, **kwargs):
		if self.start is None:
			self.start = self.term.start
		if self.end is None:
			self.end = self.term.end
		super(Officer, self).save(*args, **kwargs)

	class Meta:
		app_label = 'stepping_out'
		unique_together = ('user', 'position', 'term')


class OfficerPositionManager(models.Manager):
	def get_user_positions(self, user, termlist):
		return self.filter(users=user, users__officers__terms__in=termlist)

	def get_user_current_positions(self, user):
		return self.get_user_positions(user, Term.objects.get_current())


class OfficerPosition(models.Model):
	"""
	Officer Positions are non-generic groupings that connect users into the
	permissions framework - based on meta information such as terms of office.

	Conveniently, these positions can also be used to automatically generate a
	list of current officers, through the extended manager.
	"""
	OFFICER = 'o'
	INSTRUCTOR = 'i'
	CATEGORY_CHOICES = (
		(OFFICER, 'Officer'),
		(INSTRUCTOR, 'Instructor'),
	)
	objects = OfficerPositionManager()
	
	name = models.CharField(max_length=50)
	slug = models.SlugField(max_length=50, unique=True)
	description = models.TextField(help_text="A description of the officer's roles and responsibilities.")
	
	permissions = models.ManyToManyField(Permission, blank=True, null=True)
	order = models.IntegerField()
	category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
	users = models.ManyToManyField(User, related_name="officer_positions", through=Officer)

	def __unicode__(self):
		return self.name

	def users_for_terms(self, termlist):
		return self.users.filter(officers__terms__in=termlist)

	@property
	def current_users(self):
		return self.users_for_terms(Term.objects.get_current())

	class Meta:
		app_label = 'stepping_out'
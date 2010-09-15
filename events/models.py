from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.forms import USZipCodeField as USZipCodeFormField
from django.contrib.localflavor.us.models import USStateField
from django.contrib.sites.models import Site
from django.utils.hashcompat import sha_constructor
import datetime


class USZipCodeField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 10
		super(USZipCodeField, self).__init__(*args, **kwargs)
	
	def formfield(self, form_class=USZipCodeFormField, **kwargs):
		return super(USZipCodeField, self).formfield(form_class, **kwargs)


class Building(models.Model):
	name = models.CharField(max_length=150, blank=True)
	address = models.CharField(max_length=255)
	city = models.CharField(max_length=150)
	state = USStateField()
	zipcode = USZipCodeField()


class Venue(models.Model):
	name = models.CharField(max_length=150)
	location = models.TextField(help_text='Where in the building?', blank=True)
	building = models.ForeignKey(Building)


class Event(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	
	start_date = models.DateField()
	start_time = models.TimeField(blank=True, null=True)
	
	end_date = models.DateField()
	end_time = models.TimeField(blank=True, null=True)
	
	venue = models.ForeignKey(Venue, blank=True, null=True)
	parent_event = models.ForeignKey('self', blank=True, null=True)
	uid = models.CharField(max_length=255, unique=True)
	
	def save(self, *args, **kwargs):
		if not self.uid:
			# This isn't secret information, so don't use the secret key.
			self.uid = '%s//%s' % (
				sha_constructor(self.start_date.iso_format() + self.title + self.description),
				Site.objects.get_current().domain
			)
		super(Event, self).save(*args, **kwargs)


class Agenda(models.Model):
	event = models.OneToOneField(Event)


class AgendaItem(models.Model):
	agenda = models.ForeignKey(Agenda)
	added_by = models.ForeignKey(User, related_name='agenda_items')
	added_time = models.DateTimeField(default=datetime.datetime.now)
	title = models.CharField(max_length=100)
	description = models.TextField(blank=True)


class Minutes(models.Model):
	event = models.OneToOneField(Event)
	
	class Meta:
		verbose_name_plural = 'minutes'


class MinutesEntry(models.Model):
	minutes = models.ForeignKey(Minutes)
	added_by = models.ForeignKey(User, related_name='minutes_entries')
	added_time = models.DateTimeField(default=datetime.datetime.now)
	entry = models.TextField(blank=True)
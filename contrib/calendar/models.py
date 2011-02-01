from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from stepping_out.events.models import Event
import datetime


class Calendar(models.Model):
	name = models.CharField(max_length=100, unique=True)
	calendar_id = models.CharField("Calendar ID", max_length=100, unique=True, help_text="Should conform to Formal Public Identifier format.")
	sync_with_url = models.URLField(help_text='Valid URL of an ics (ICal) file', blank=True)
	events = models.ManyToManyField(Event, blank=True, null=True)
	
	def __unicode__(self):
		return self.name


class Ride(models.Model):
	driver = models.ForeignKey(User, related_name='ride_driver_set')
	passengers = models.ManyToManyField(User, related_name='ride_passenger_set')
	event = models.ForeignKey(Event, related_name='rides')
	
	seats = models.PositiveIntegerField()
	meeting_time = models.DateTimeField(blank=True, null=True)
	meeting_place = models.TextField(blank=True)
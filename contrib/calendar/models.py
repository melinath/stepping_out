from django.contrib.auth.models import User
from django.db import models
from stepping_out.events.models import Event


class Calendar(models.Model):
	name = models.CharField(max_length=100, unique=True)
	prodid = models.CharField(max_length=100, unique=True)
	sync_with_url = models.URLField(help_text='Valid URL of an ics (ICal) file')
	last_modified = models.DateTimeField()
	events = models.ManyToManyField(Event)


class Ride(models.Model):
	driver = models.ForeignKey(User, related_name='ride_driver_set')
	passengers = models.ManyToManyField(User, related_name='ride_passenger_set')
	event = models.ForeignKey(Event)
	
	seats = models.PositiveIntegerField()
	time = models.DateTimeField(blank=True, null=True)
	place = models.TextField(blank=True)
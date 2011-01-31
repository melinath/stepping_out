from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.forms import USZipCodeField as USZipCodeFormField
from django.contrib.localflavor.us.models import USStateField
from django.contrib.sites.models import Site
from django.core.validators import RegexValidator
from django.http import HttpResponseRedirect
from django.utils.hashcompat import sha_constructor
import datetime

NOTE = '0'
AGENDA = '1'
MINUTES = '2'
NOTE_TYPE_CHOICES = (
	(NOTE, 'Note'),
	(AGENDA, 'Agenda Item'),
	(MINUTES, 'Minutes Entry'),
)


class USZipCodeField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 10
		super(USZipCodeField, self).__init__(*args, **kwargs)
	
	def formfield(self, form_class=USZipCodeFormField, **kwargs):
		return super(USZipCodeField, self).formfield(form_class, **kwargs)


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^stepping_out\.events\.models\.USZipCodeField"])


class Building(models.Model):
	name = models.CharField(max_length=150, blank=True)
	address = models.CharField(max_length=255)
	city = models.CharField(max_length=150)
	state = USStateField()
	zipcode = USZipCodeField()


class Venue(models.Model):
	name = models.CharField(max_length=150)
	location = models.TextField(help_text='Second floor, on the hill, etc.', blank=True)
	building = models.ForeignKey(Building, blank=True, null=True)


class Attendance(models.Model):
	event = models.ForeignKey('Event')
	user = models.ForeignKey(User)
	
	RSVP_CHOICES = (
		('y', 'Yes'),
		('n', 'No'),
		('m', 'Maybe'),
	)
	rsvp = models.CharField(max_length=1, choices=RSVP_CHOICES, blank=True)
	# Cmp workshop models... pricing information could go on this model!
	# so could ride information... though that could also be a "third-party"
	# add-on


class Event(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	
	start_date = models.DateField(help_text="YYYY-MM-DD")
	start_time = models.TimeField(blank=True, null=True, help_text="HH:MM:SS - 24 hour clock")
	
	end_date = models.DateField()
	end_time = models.TimeField(blank=True, null=True)
	
	venue = models.ForeignKey(Venue, blank=True, null=True)
	parent_event = models.ForeignKey('self', blank=True, null=True)
	uid = models.CharField(max_length=255, unique=True, blank=True,
		help_text="This will be auto-generated if left blank.",
		validators=[RegexValidator(r"^[\w-]+//[^/]+$")])
	#TODO: Handle repetition rules.
	
	owner = models.ForeignKey(User, related_name="events")
	# editors = models.ManyToManyField(User, blank=True, null=True)
	attendees = models.ManyToManyField(User, through=Attendance, related_name="attended_events")
	
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	
	def save(self, *args, **kwargs):
		if not self.uid:
			self.uid = self.generate_uid()
		super(Event, self).save(*args, **kwargs)
	
	def generate_uid(self):
		# could potentially return a more human-readable uid...?
		return "%s//%s" % (
				sha_constructor(self.start_date.isoformat() + datetime.datetime.now().isoformat() + self.title + self.description).hexdigest()[::2],
				Site.objects.get_current().domain
			)
	
	def __unicode__(self):
		return self.title


class EventNote(models.Model):
	event = models.ForeignKey(Event)
	note_type = models.CharField(max_length=1, default=NOTE, choices=NOTE_TYPE_CHOICES)
	user = models.ForeignKey(User, related_name='event_notes')
	timestamp = models.DateTimeField(auto_now_add=True)
	content = models.TextField()
	
	def __unicode__(self):
		return "%s :: %s :: %s" % (self.event, self.user, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
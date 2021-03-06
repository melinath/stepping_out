from datetime import datetime, date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.localflavor.us.models import PhoneNumberField
from django.core.validators import MinLengthValidator, RegexValidator
from stepping_out.pricing.models import PricePackage, Price, Payment
from stepping_out.pricing.people import registry
import random
import string


REGISTRATION_KEY_CHARACTERS = string.ascii_letters + string.digits
REGISTRATION_KEY_LENGTH = 6


class WorkshopManager(models.Manager):
	def create_basic(self, name, tagline=''):
		"""
		Creates and returns a "basic workshop". This includes a workshop and
		related price packages and housing coordinator.
		"""
		today = date.today()
		workshop = self.create(name=name, tagline=tagline,
			registration_start=today, online_registration_end=today + timedelta(14),
			workshop_start=today + timedelta(21), workshop_end=today+timedelta(24),
			is_active=False)
		
		earlybird = workshop.price_packages.create(name='Earlybird',
			available_until=today + timedelta(7), person_types=registry._registry.keys())
		earlybird.options.create(name='Full Weekend')
		earlybird.options.create(name='Saturday only')
		earlybird.options.create(name='Sunday only')
		
		online = workshop.price_packages.create(name='Online',
			person_types=registry._registry.keys())
		online.options.create(name='Full Weekend')
		online.options.create(name='Saturday only')
		online.options.create(name='Sunday only')
		
		atd = workshop.price_packages.create(name='At the door',
			person_types=registry._registry.keys())
		atd.options.create(name='Full Weekend')
		atd.options.create(name='Saturday only')
		atd.options.create(name='Sunday only')
		
		alc = workshop.price_packages.create(name='A la carte',
			person_types=registry._registry.keys())
		alc.options.create(name='Lesson')
		alc.options.create(name='Friday night dance')
		alc.options.create(name='Saturday night dance')
		alc.options.create(name='Farewell dance')
		
		return workshop


class Workshop(models.Model):
	name = models.CharField(max_length=150)
	tagline = models.CharField(max_length=255, blank=True)
	registration_start = models.DateField(verbose_name='registration opens', help_text='Opens at 00:00:01')
	online_registration_end = models.DateField(verbose_name='online registration closes', help_text='Closes at 23:59:59')
	workshop_start = models.DateField(verbose_name='workshop start date')
	workshop_end = models.DateField(verbose_name='workshop end date')
	registered_users = models.ManyToManyField(User, through='Registration')
	is_active = models.BooleanField()
	
	price_packages = generic.GenericRelation(PricePackage, content_type_field='event_content_type', object_id_field='event_object_id')
	
	objects = WorkshopManager()
	
	def __unicode__(self):
		return self.name
	
	@property
	def registration_is_open(self):
		return self.is_active and (self.registration_start <= date.today() <= self.online_registration_end)
	
	class Meta:
		get_latest_by = 'workshop_start'


class WorkshopTrack(models.Model):
	workshop = models.ForeignKey(Workshop, related_name='tracks')
	name = models.CharField(max_length=75)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		unique_together = ('workshop', 'name')


class Registration(models.Model):
	DANCING_AS_CHOICES = (
		('l', 'Lead'),
		('f', 'Follow')
	)
	workshop = models.ForeignKey(Workshop)
	track = models.ForeignKey(WorkshopTrack)
	
	user = models.ForeignKey(User, blank=True, null=True)
	dancing_as = models.CharField(max_length=1, choices=DANCING_AS_CHOICES)
	registered_at = models.DateTimeField(default=datetime.now)
	price = models.ForeignKey(Price)
	
	key = models.CharField(max_length=REGISTRATION_KEY_LENGTH, validators=[MinLengthValidator(REGISTRATION_KEY_LENGTH), RegexValidator(r"[%s]" % REGISTRATION_KEY_CHARACTERS)])
	first_name = models.CharField(max_length=30, blank=True)
	last_name = models.CharField(max_length=30, blank=True)
	email = models.EmailField(blank=True)
	phone_number = PhoneNumberField(blank=True)
	
	@property
	def total_paid(self):
		return self.payments.aggregate(models.Sum('paid'))['paid__sum'] or 0
	
	def make_key(self):
		while True:
			new_key = ''.join(random.sample(REGISTRATION_KEY_CHARACTERS, REGISTRATION_KEY_LENGTH))
			try:
				Registration.objects.exclude(pk=self.pk).get(key=new_key)
			except Registration.DoesNotExist:
				return new_key
	
	def get_full_name(self):
		if self.user and self.user.get_full_name():
			return self.user.get_full_name()
		elif self.first_name and self.last_name:
			return " ".join([self.first_name, self.last_name])
		elif self.user:
			return self.user.username
		return self.key
	
	def __unicode__(self):
		return u"%s - %s" % (self.get_full_name(), self.workshop)
	
	class Meta:
		# If user is None, will that trigger unique checks?
		unique_together = (('workshop', 'user'), ('workshop', 'key'))
		ordering = ('-registered_at',)


class WorkshopEvent(models.Model):
	title = models.CharField(max_length=150)
	description = models.TextField()
	start = models.DateTimeField()
	end = models.DateTimeField()
	track = models.ForeignKey(WorkshopTrack, blank=True, null=True)
	workshop = models.ForeignKey(Workshop)
	
	def save(self, *args, **kwargs):
		if self.track and self.track.workshop != self.workshop:
			self.workshop = self.track.workshop
		super(WorkshopEvent, self).save(*args, **kwargs)


class HousingOffer(models.Model):
	registration = models.OneToOneField(Registration)
	address = models.TextField()
	smoking = models.BooleanField(verbose_name='Smoking or recent smoking')
	cats = models.BooleanField()
	dogs = models.BooleanField()
	num_ideal = models.PositiveIntegerField(verbose_name='Ideal number of guests', default=2)
	num_max = models.PositiveIntegerField(verbose_name='Maximum number of guests', default=3)
	comments = models.TextField(verbose_name='Additional comments', blank=True)
	
	class Meta:
		verbose_name = "Housing Offer"
		verbose_name_plural = "Offered Housing"


class HousingRequest(models.Model):
	registration = models.OneToOneField(Registration)
	PREFERENCE_CHOICES = (
		(0, "I don't care"),
		(1, "Preferred"),
		(2, "A must!"),
	)
	nonsmoking = models.IntegerField(max_length=1, choices=PREFERENCE_CHOICES)
	no_cats = models.IntegerField(max_length=1, choices=PREFERENCE_CHOICES)
	no_dogs =  models.IntegerField(max_length=1, choices=PREFERENCE_CHOICES)
	housed_with = models.ForeignKey(HousingOffer, blank=True, null=True, related_name='housed')
	comments = models.TextField(verbose_name='Additional comments', blank=True)
	
	class Meta:
		verbose_name = "Housing Request"
		verbose_name_plural = "Requested Housing"
from datetime import datetime, date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from stepping_out.pricing.models import PricePackage
from stepping_out.pricing.people import registry
from stepping_out.housing.models import HousingCoordinator


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
	registered_users = models.ManyToManyField(User, through='WorkshopUserMetaInfo')
	is_active = models.BooleanField()
	
	price_packages = generic.GenericRelation(PricePackage, content_type_field='event_content_type', object_id_field='event_object_id')
	_housing = generic.GenericRelation(HousingCoordinator, content_type_field='event_content_type', object_id_field='event_object_id')
	
	objects = WorkshopManager()
	
	@property
	def housing(self):
		# going for a "GenericOneToOne" feel here.
		if self._housing.all():
			return self._housing.all()[0]
		return None
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		get_latest_by = ['workshop_start']


class WorkshopUserMetaInfo(models.Model):
	DANCING_AS_CHOICES = (
		('l', 'Lead'),
		('f', 'Follow')
	)
	workshop = models.ForeignKey(Workshop)
	user = models.ForeignKey(User)
	dancing_as = models.CharField(max_length=1, choices=DANCING_AS_CHOICES)
	registered_at = models.DateTimeField(default=datetime.now)
	
	class Meta:
		unique_together = ('workshop', 'user')


class WorkshopEvent(models.Model):
	title = models.CharField(max_length=150)
	description = models.TextField()
	start = models.DateTimeField()
	end = models.DateTimeField()
	workshop = models.ForeignKey(Workshop)
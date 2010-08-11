from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from stepping_out.pricing.models import PricePackage, PriceClass
from stepping_out.housing.models import HousingCoordinator


class WorkshopUserMetaInfo(models.Model):
	PAYMENT_CHOICES = (
		('cash', 'Cash'),
		('check', 'Check'),
		('online', 'Online')
	)
	DANCING_AS_CHOICES = (
		('l', 'Lead'),
		('f', 'Follow')
	)
	workshop = models.ForeignKey('Workshop')
	user = models.ForeignKey(User)
	# FIXME: Choices should be limited to the classes available for the workshop.
	price_class = models.ForeignKey(PriceClass)
	paid = models.FloatField(verbose_name="Amount paid") # FIXME: precision
	payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
	dancing_as = models.CharField(max_length=1, choices=DANCING_AS_CHOICES)
	registered = models.DateTimeField(default=datetime.now)


class Workshop(models.Model):
	name = models.CharField(max_length=150)
	tagline = models.CharField(max_length=255, blank=True)
	registration_start = models.DateField(verbose_name='registration opens', help_text='Opens at 00:00:01')
	online_registration_end = models.DateField(verbose_name='online registration closes', help_text='Closes at 23:59:59')
	workshop_start = models.DateField(verbose_name='workshop start date')
	workshop_end = models.DateField(verbose_name='workshop end date')
	registered_users = models.ManyToManyField(User, through=WorkshopUserMetaInfo)
	
	prices = generic.GenericRelation(PricePackage, content_type_field='event_content_type', object_id_field='event_object_id')
	_housing = generic.GenericRelation(HousingCoordinator, content_type_field='event_content_type', object_id_field='event_object_id')
	
	@property
	def housing(self):
		# going for a "GenericOneToOne" feel here.
		return self._housing.all()[0]
	
	class Meta:
		get_latest_by = ['workshop_start']


class WorkshopEvent(models.Model):
	title = models.CharField(max_length=150)
	description = models.TextField()
	start = models.DateTimeField()
	end = models.DateTimeField()
	workshop = models.ForeignKey(Workshop)
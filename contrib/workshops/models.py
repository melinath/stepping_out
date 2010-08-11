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
	# FIXME: F() limit_to the classes in the workshop's packages. Note this
	# generally will not be manually set like this.
	price_class = models.ForeignKey(PriceClass)
	paid = models.FloatField(verbose_name="Amount paid") # FIXME: precision
	payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
	dancing_as = models.CharField(max_length=1, choices=DANCING_AS_CHOICES)


class Workshop(models.Model):
	name = models.CharField(max_length=150)
	tagline = models.CharField(max_length=255, blank=True)
	early_registration_start = models.DateField(blank=True, null=True)
	
	# FIXME: Add validation w/ F() objects to make sure dates are correctly
	# ordered.
	# Could potentially have a separate date model, but seems overly complex.
	normal_registration_start = models.DateField()
	online_registration_end = models.DateField()
	workshop_start = models.DateField()
	workshop_end = models.DateField()
	registered_users = models.ManyToManyField(User, through=WorkshopUserMetaInfo)
	prices = generic.GenericRelation(PricePackage, content_type_field='attached_content_type', object_id_field='attached_object_id')
	housing = generic.GenericRelation(HousingCoordinator, content_type_field='event_content_type', object_id_field='event_object_id')
	
	class Meta:
		get_latest_by = ['workshop_start']


class WorkshopEvent(models.Model):
	title = models.CharField(max_length=150)
	description = models.TextField()
	start = models.DateTimeField()
	end = models.DateTimeField()
	workshop = models.ForeignKey(Workshop)
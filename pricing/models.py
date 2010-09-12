from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from paypal.standard.ipn.models import PayPalIPN
from stepping_out.pricing import people
from stepping_out.pricing.fields import SlugListField
import datetime

class PricePackage(models.Model):
	"""
	A price package can be attached to anything: a lesson, a dance, a workshop.
	May later be explicity limited to any 'event'.
	Price packages are, for example, "Earlybird", "Online", "At the Door",
	"A la carte"
	"""
	name = models.CharField(max_length=40)
	description = models.TextField(blank=True)
	event_content_type = models.ForeignKey(ContentType)
	event_object_id = models.PositiveIntegerField()
	event = generic.GenericForeignKey('event_content_type', 'event_object_id')
	available_until = models.DateField(blank=True, null=True)
	person_types = SlugListField(choices=people.registry.get_choices)
	
	def __unicode__(self):
		return '%s :: %s' % (self.name, self.event)
	
	def save(self, *args, **kwargs):
		refresh = False
		if self.pk:
			old = self._default_manager.get(pk=self.pk)
			if old.person_types != self.person_types:
				refresh = True
		
		super(PricePackage, self).save(*args, **kwargs)
		
		if refresh:
			for option in self.options.all():
				option.refresh_person_types()
	
	class Meta:
		app_label = 'stepping_out'
		ordering = ['available_until']


class PriceOption(models.Model):
	"""
	A price option is, for example, "Full Weekend", "Saturday", "Friday Night
	Dance".
	"""
	name = models.CharField(max_length=40)
	package = models.ForeignKey(PricePackage, related_name='options')
	
	def __unicode__(self):
		return self.name
	
	def refresh_person_types(self):
		for person_type in self.package.person_types:
			self.prices.get_or_create(person_type=person_type)
		
		for price in self.prices.exclude(person_type__in=self.package.person_types):
			price.delete()
	
	def save(self, *args, **kwargs):
		super(PriceOption, self).save(*args, **kwargs)
		self.refresh_person_types()
	save.alters_data = True
	
	class Meta:
		app_label = 'stepping_out'


class Price(models.Model):
	option = models.ForeignKey(PriceOption, related_name='prices')
	person_type = models.CharField(max_length=15, editable=False)
	price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	
	def get_person_type(self):
		return people.registry[self.person_type]
	
	def get_event(self):
		return self.option.package.event
	
	class Meta:
		app_label = 'stepping_out'
		unique_together = ['option', 'person_type']


class Payment(models.Model):
	PAYMENT_CHOICES = (
		('cash', 'Cash'),
		('check', 'Check'),
		('online', 'Online')
	)
	payment_for_id = models.PositiveIntegerField()
	payment_for_ct = models.ForeignKey(ContentType)
	payment_for = generic.GenericForeignKey('payment_for_ct', 'payment_for_id')
	user = models.ForeignKey(User)
	paid = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Amount paid")
	payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
	payment_made = models.DateTimeField(default=datetime.datetime.now)
	ipn = models.OneToOneField(PayPalIPN, blank=True, null=True)
	
	class Meta:
		app_label = 'stepping_out'
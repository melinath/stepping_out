from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from stepping_out.pricing import people
from stepping_out.pricing.fields import SlugListField


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
	person_types = SlugListField(choices=people.registry.get_choices())
	
	def __unicode__(self):
		return '%s :: %s' % (self.name, self.event)
	
	class Meta:
		app_label = 'stepping_out'


class PriceClass(models.Model):
	"""
	A price class is, for example, "Full Weekend", "Saturday", "Friday Night
	Dance".
	"""
	name = models.CharField(max_length=40)
	package = models.ForeignKey(PricePackage, related_name='price_classes')
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		super(PriceClass, self).save(*args, **kwargs)
		for person_type in self.package.person_types:
			self.prices.get_or_create(person_type=person_type)
		
		for price in self.prices.exclude(person_type__in=self.package.person_types):
			price.delete()
	save.alters_data = True
	
	class Meta:
		app_label = 'stepping_out'
		verbose_name_plural = 'price classes'


class Price(models.Model):
	price_class = models.ForeignKey(PriceClass, related_name='prices')
	person_type = models.CharField(max_length=15, editable=False)
	price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	
	def get_person_type(self):
		return people.registry[self.person_type]
	
	class Meta:
		app_label = 'stepping_out'
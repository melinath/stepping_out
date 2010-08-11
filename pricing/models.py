from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class PricePackage(models.Model):
	"""
	A price package can be attached to anything: a lesson, a dance, a workshop.
	May later be limited to any 'event'.
	"""
	name = models.CharField(max_length=40)
	description = models.TextField(blank=True)
	event_content_type = models.ForeignKey(ContentType)
	event_object_id = models.PositiveIntegerField()
	event = generic.GenericForeignKey('event_content_type', 'event_object_id')
	available_until = models.DateField(blank=True, null=True)
	
	class Meta:
		app_label = 'stepping_out'


class PriceClass(models.Model):
	package = models.ForeignKey(PricePackage, related_name='prices')
	name = models.CharField(max_length=40)
	price = models.FloatField()  # FIXME: how to set float precision?
	
	class Meta:
		app_label = 'stepping_out'


#class PackageItem(models.Model):
#	# Or should I just have an "includes" text field? Is a rel to the actual
#	# objects (if they exist) even useful?
#	package = models.ForeignKey(PricePackage, related_name='package_items')
#	item_content_type = models.ForeignKey(ContentType)
#	item_object_id = models.PositiveIntegerField()
#	item = generic.GenericForeignKey('item_content_type', 'item_object_id')
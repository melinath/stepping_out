from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class PricePackage(models.Model):
	name = models.CharField(max_length=40)
	description = models.TextField(blank=True)
	attached_content_type = models.ForeignKey(ContentType)
	attached_object_id = models.PositiveIntegerField()
	attached_to = generic.GenericForeignKey('attached_content_type', 'attached_object_id')
	
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
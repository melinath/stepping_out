"""
Workshop-related models that interact with auth.
"""


from django.db import models
from django.contrib.auth.models import User


__all__ = (
	'WorkshopProfile',
	'HousingProfile',
	'HousingPreferencesProfile'
)


class WorkshopProfile(models.Model):
	student = models.BooleanField()
	user = models.OneToOneField(User)
	
	# needs to authenticate properly - probably custom is better. Should check
	# against student status and email.
	zip_or_ocmr = models.CharField(max_length=10,verbose_name='Zip or OCMR')
	
	class Meta:
		app_label = 'stepping_out'


class HousingProfile(models.Model):
	# perhaps TextField to allow multi-line addresses if necessary?
	# for now though this is fine.
	address = models.CharField(max_length=200)
	smoking = models.BooleanField(help_text = 'Smoking or recent smoking')
	cats = models.BooleanField()
	dogs = models.BooleanField()
	user = models.OneToOneField(User)
	
	class Meta:
		app_label = 'stepping_out'


class HousingPreferencesProfile(models.Model):
	PREFERENCE_CHOICES = (
		(0, "I don't care"),
		(1, "Preferred"),
		(2, "A must!"),
	)
	nonsmoking = models.IntegerField(max_length=2, choices = PREFERENCE_CHOICES)
	no_cats = models.IntegerField(max_length=2, choices = PREFERENCE_CHOICES)
	no_dogs =  models.IntegerField(max_length=2, choices = PREFERENCE_CHOICES)
	user = models.OneToOneField(User)
	
	class Meta:
		verbose_name = verbose_name_plural = "Housing Preferences"
		app_label = 'stepping_out'
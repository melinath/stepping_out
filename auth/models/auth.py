"""
Models which are strictly auth-related.
"""


from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.localflavor.us.models import PhoneNumberField
from datetime import datetime


__all__ = (
	'Term',
	'OfficerUserMetaInfo',
	'OfficerPosition'
)


PhoneNumberField(blank=True).contribute_to_class(User, 'phone_number')


class Term(models.Model):
	start = models.DateField()
	end = models.DateField()
	name = models.CharField(max_length=30, blank = True)
	
	def __unicode__(self):
		if(self.name):
			return self.name
			
		return "%s -> %s" % (self.start,self.end)
	
	class Meta:
		app_label = 'stepping_out' 


class OfficerUserMetaInfo(models.Model):
	officer_position = models.ForeignKey('OfficerPosition')
	user = models.ForeignKey(User)
	terms = models.ManyToManyField(Term)
	
	class Meta:
		verbose_name = 'Officer/User Meta Info'
		verbose_name_plural = 'Officer/User Meta Info'
		app_label = 'stepping_out'
		
	def __unicode__(self):
		return '%s :: %s' % (self.user.get_full_name(), self.officer_position)


class ExtendedOfficerPositionManager(models.Manager):
	"""
	I need to be able to return:
		1. - A list of all users who are currently officers.
		   - A list of users who currently occupy an arbitrarily named position
		2. - A list of all (officerposition, user_list) tuples
		   - The (officerposition, user_list) tuple for an arbitrary position
	"""
		
	def get_current_terms(self):
		return Term.objects.exclude(
			start__gt=datetime.now
		).exclude(
			end__lt=datetime.now
		)
		
	def get_results_for_terms(self, termlist, func, *args, **kwargs):
		"""Where termlist is a list of Term objects."""
		result_set = set()
		for term in termlist:
			for meta in term.officerusermetainfo_set.all():
				result_set |= func(meta, *args, **kwargs)
		
		return result_set
		
	def get_positions_for_terms(self, termlist):
		def func(meta):
			return set([meta.officer_position])
		return self.get_results_for_terms(termlist, func)
				
	def get_users_for_terms(self, termlist, position = None):
		def func(meta, position):
			if position == None or position == meta.officer_position.name:
				return set([meta.user])
			return set()
		return self.get_results_for_terms(termlist, func, position)
			
	def get_tuples_for_terms(self, termlist, position = None):
		def func(meta, position):
			if position == None or position == meta.officer_position.name:
				return set([(meta.user, meta.officer_position)])
			return set()
		return self.get_results_for_terms(termlist, func, position)
		
	def get_list_for_terms(self, termlist, position = None, sort=True):
		tuples = self.get_tuples_for_terms(termlist, position)
		officer_dict = {}
		officer_list = []
		for tuple in tuples:
			try:
				assert officer_dict[tuple[1]]
			except KeyError:
				officer_dict[tuple[1]] = set()
			officer_dict[tuple[1]].add(tuple[0])
		
		for position in officer_dict:
			officer_list.append((position, officer_dict[position]))
		
		if sort is True:
			return sorted(officer_list, key=lambda officer: officer[0].order)
			
		return officer_list
		
	def get_current_users(self, *args, **kwargs):
		return self.get_users_for_terms(self.get_current_terms(), *args, **kwargs)
		
	def get_current_tuples(self, *args, **kwargs):
		return self.get_tuples_for_terms(self.get_current_terms(), *args, **kwargs)
		
	def get_current_list(self, *args, **kwargs):
		return self.get_list_for_terms(self.get_current_terms(), *args, **kwargs)
		

class OfficerPosition(models.Model):
	"""
	Officer Positions are non-generic groupings that connect users into the
	permissions framework - based on meta information such as terms of office.
	
	Conveniently, these positions can also be used to automatically generate a
	list of current officers, through the extended manager.	  
	"""
	name = models.CharField(max_length=50)
	permissions = models.ManyToManyField(Permission, blank=True, null=True)
	order = models.IntegerField()
	users = models.ManyToManyField(User, through='OfficerUserMetaInfo')
	objects = ExtendedOfficerPositionManager()
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		app_label = 'stepping_out'
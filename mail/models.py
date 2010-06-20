from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.contrib.sites.models import Site
from stepping_out.mail.validators import EmailNameValidator


SUBSCRIPTION_CHOICES = (
	('mod', 'Moderators',),
	('sub', 'Subscribers',),
	('all', 'Anyone',),
)


class UserList(models.Model):
	"Still need validation"
	name = models.CharField(max_length = 50)
	content_type = models.ForeignKey(ContentType)
	manager = models.CharField(
		max_length=30,
		help_text = "The manager's method must return a set of users. Default manager: objects.",
		blank = True
	)
	method = models.CharField(
		max_length=30,
		help_text = "The manager's method must return a set of users. Default method: all",
		blank = True
	)
	arg = models.CharField(
		max_length=30,
		blank = True,
		help_text = "The manager method may take a single string argument."
	)
	
	def __unicode__(self):
		return self.name
		
	def compile(self):
		model = self.content_type.model_class()
		manager = self.manager or u'objects'
		method = self.method or u'all'
		arg = self.arg
		
		function = model.__dict__[manager].manager.__getattribute__(method)
		
		if arg:
			return function(arg)
		else:
			return function()


class MailingListManager(models.Manager):
	def by_domain(self):
		"""
		Returns a dictionary of MailingList objects by domain and address.
		"""
		mlists = self.all()
		by_domain = {}
		for mlist in mlists:
			if mlist.site.domain not in by_domain:
				by_domain[mlist.site.domain] = {}
			
			by_domain[mlist.site.domain][mlist.address] = mlist
		
		return by_domain


class MailingList(models.Model):
	"""
	This model contains all options for a mailing list, as well as some helpful
	methods for accessing subscribers, moderators, etc.
	"""
	name = models.CharField(max_length=50)
	address = models.CharField(max_length=100, validators=[EmailNameValidator()])
	site = models.ForeignKey(Site, verbose_name="@", default=Site.objects.get_current())
	objects = MailingListManager()
	
	subscribed_users = models.ManyToManyField(
		User,
		related_name = 'subscribed_mailinglist_set',
		blank = True,
		null = True,
		verbose_name = 'users'
	)
	subscribed_groups = models.ManyToManyField(
		Group,
		related_name = 'subscribed_mailinglist_set',
		blank = True,
		null = True,
		verbose_name = 'groups'
	)
	subscribed_userlists = models.ManyToManyField(
		UserList,
		related_name = 'subscribed_mailinglist_set',
		blank = True,
		null = True,
		verbose_name = 'user lists'
	)
	
	who_can_post = models.CharField(
		max_length = 3,
		choices = SUBSCRIPTION_CHOICES
	)
	self_subscribe_enabled = models.BooleanField(
		verbose_name = 'self-subscribe enabled'
	)
	
	moderator_users = models.ManyToManyField(
		User,
		related_name = 'moderated_mailinglist_set',
		blank = True,
		null = True,
		verbose_name = 'users'
	)
	moderator_groups = models.ManyToManyField(
		Group,
		related_name='moderated_mailinglist_set',
		blank = True,
		null = True,
		verbose_name = 'groups'
	)
	moderator_userlists = models.ManyToManyField(
		UserList,
		related_name='moderated_mailinglist_set',
		blank = True,
		null = True,
		verbose_name = 'user lists'
	)
	
	def __unicode__(self):
		return self.name
	
	def remove_user(self, user):
		"""
		user should be a user instance. This will take a user off the list.
		Is this actually useful?
		"""
		pass
	
	def add_user(self, user):
		"""
		user should be a user instance. This will add a user to the list.
		"""
		pass
	
	@property
	def subscribers(self):
		return self.get_user_set('subscribed')
	
	@property
	def moderators(self):
		return self.get_user_set('moderator')
	
	@property
	def recipients(self):
		return self.subscribers | self.moderators
		
	def get_user_set(self, prefix):
		userset = set(getattr(self, '%s_users' % prefix).all())
		for group in getattr(self, '%s_groups' % prefix).all():
			userset |= set(group.user_set.all())
			
		for userlist in getattr(self, '%s_userlists' % prefix).all():
			userset |= set(userlist.compile())
			
		return userset
		
	def can_post(self, user):
		if self.who_can_post == 'all':
			return True
			
		if self.who_can_post == 'sub' and user in self.subscribers:
			return True
		
		if user in self.moderators:
			return True
		
		return False
	
	@property
	def full_address(self):
		return '%s@%s' % (self.address, self.site.domain)
	
	class Meta:
		unique_together = ('site', 'address',)
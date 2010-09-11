from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import simplejson as json
from stepping_out.mail.validators import EmailNameValidator
from stepping_out.mail.userlists import UserListPlugin


SUBSCRIPTION_CHOICES = (
	('mod', 'Moderators',),
	('sub', 'Subscribers',),
	('all', 'Anyone',),
)


class UserEmail(models.Model):
	email = models.EmailField(unique=True)
	user = models.ForeignKey(User, related_name='emails', blank=True, null=True)
	
	def delete(self):
		user = self.user
		super(UserEmail, self).delete()
		if user and user.email == self.email:
			user.email = user.emails.all()[0].email
	
	def __unicode__(self):
		return self.email
	
	class Meta:
		app_label = 'mail'


def validate_user_emails(sender, **kwargs):
	instance = kwargs['instance']
	try:
		User.objects.exclude(pk=instance.pk).get(emails__email=instance.email)
	except User.DoesNotExist:
		pass
	else:
		raise ValidationError('A user with that email already exists.')


def sync_user_emails(instance, created, **kwargs):
	if not created:
		instance.emails.get_or_create(email=instance.email)


models.signals.pre_save.connect(validate_user_emails, sender=User)
models.signals.post_save.connect(sync_user_emails, sender=User)


class UserList(models.Model):
	USERLIST_CHOICES = [(k,unicode(v.__name__)) for k,v in UserListPlugin.plugins.items()]
	name = models.CharField(max_length = 50)
	plugin = models.CharField(
		max_length = 20,
		blank=True,
		choices=USERLIST_CHOICES
	)
	json_value = models.TextField(
		max_length=30,
		blank = True,
		help_text = "JSON - to be passed as an arg."
	)
	
	def get_value(self):
		if self.json_value == '':
			return None
		return json.loads(self.json_value)
	
	def set_value(self, value):
		self.json_value = json.dumps(value)
	
	def delete_value(self):
		self.json_value = json.dumps(None)
	
	value = property(get_value, set_value, delete_value)
	
	def get_list(self):
		if not hasattr(self, '_list'):
			self._list = UserListPlugin.plugins[self.plugin](self.value)
		
		return self._list.get_list()
	
	list = property(get_list)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		app_label = 'mail'


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
	# Really this whole address/site thing is ridiculous, but I don't have the
	# time just now to fix it.
	DEFAULT_SITE = None
	objects = MailingListManager()
	
	name = models.CharField(max_length=50)
	address = models.CharField(max_length=100, validators=[EmailNameValidator()])
	site = models.ForeignKey(Site, verbose_name="@", default=DEFAULT_SITE)
	help_text = models.TextField(verbose_name='description', blank=True)
	
	subscribed_users = models.ManyToManyField(
		User,
		related_name = 'subscribed_mailinglist_set',
		blank = True,
		null = True
	)
	subscribed_groups = models.ManyToManyField(
		Group,
		related_name = 'subscribed_mailinglist_set',
		blank = True,
		null = True
	)
	subscribed_userlists = models.ManyToManyField(
		UserList,
		related_name = 'subscribed_mailinglist_set',
		blank = True,
		null = True
	)
	subscribed_emails = models.ManyToManyField(
		UserEmail,
		related_name = 'subscribed_mailinglist_set',
		blank = True,
		null = True
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
		null = True
	)
	moderator_groups = models.ManyToManyField(
		Group,
		related_name='moderated_mailinglist_set',
		blank = True,
		null = True
	)
	moderator_userlists = models.ManyToManyField(
		UserList,
		related_name='moderated_mailinglist_set',
		blank = True,
		null = True
	)
	
	def __unicode__(self):
		return self.name
	
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
			userset |= set(userlist.list)
			
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
		app_label = 'mail'
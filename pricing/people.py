from django.db.models.options import get_verbose_name as convert_camelcase
from django.template.defaultfilters import capfirst


class PersonMetaclass(type):
	def __new__(cls, name, bases, attrs):
		if 'slug' not in attrs:
			attrs['slug'] = name.lower()
		if 'verbose_name' not in attrs:
			attrs['verbose_name'] = capfirst(convert_camelcase(name))
		return super(PersonMetaclass, cls).__new__(cls, name, bases, attrs)


class Person(object):
	__metaclass__ = PersonMetaclass
	order = 0
	
	def validate(self, user):
		return True
	
	def __unicode__(self):
		return self.verbose_name


class AlreadyRegistered(Exception):
	pass


class NotRegistered(Exception):
	pass


class PersonRegistry(object):
	def __init__(self):
		self._registry = {}
	
	def __getitem__(self, key):
		return self._registry.__getitem__(key)
	
	def register(self, cls, slug=None):
		if slug is None:
			slug = cls.slug
		if slug in self._registry and not isinstance(self._registry[slug], cls):
			raise AlreadyRegistered("A class besides '%s' is already registered as '%s'" % (cls.__name__, slug))
		self._registry[slug] = cls()
	
	def unregister(self, cls, slug=None):
		if slug is None:
			slug = cls.slug
		if slug not in self._registry:
			raise NotRegistered("'%s' is not a registered person type" % cls.__name__)
		
		if not isinstance(self._registry[slug], cls):
			raise NotRegistered("'%s' is not registered as '%s'" % (cls.__name__, slug))
		
		del(self._registry[slug])
	
	def iterchoices(self):
		for slug, instance in self._registry.iteritems():
			yield slug, unicode(instance)


class Anyone(Person):
	order = 10


class Student(Person):
	order = 20


class NonStudent(Person):
	order = 30
	verbose_name = 'Non-student'


class PersonWithDomainEmail(Person):
	domains = []
	
	def validate(self, user):
		for email in user.user_emails.all():
			address, domain = email.split('@')
			if domain in self.domains:
				return True
		return False


registry = PersonRegistry()
registry.register(Anyone)
registry.register(Student)
registry.register(NonStudent)
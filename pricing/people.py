from django.db.models.options import get_verbose_name as convert_camelcase
from django.template.defaultfilters import capfirst


class Person(object):
	order = 0
	
	def validate(self, user):
		return True
	
	def __unicode__(self):
		return capfirst(getattr(self, 'verbose_name', convert_camelcase(self.__class__.__name__)))


class AlreadyRegistered(Exception):
	pass


class NotRegistered(Exception):
	pass


class PersonRegistry(object):
	def __init__(self):
		self._registry = {}
	
	def __getitem__(self, key):
		return self._registry.__getitem__(key)
	
	def register(self, cls):
		if issubclass(cls, Person):
			slug = unicode(getattr(cls, 'slug', cls.__name__.lower()))
			if slug in self._registry and not isinstance(self._registry[slug], cls):
				raise AlreadyRegistered("Another class is already registered as %s" % slug)
			self._registry[slug] = cls()
	
	def unregister(self, cls):
		slug = unicode(getattr(cls, 'slug', cls.__name__.lower()))
		if slug in self._registry:
			if not isinstance(self._registry[slug], cls):
				raise NotRegistered("%s is registered as %s, not %s" % (self._registry[slug], slug, cls))
			del(self._registry[slug])
	
	def get_choices(self):
		return tuple(self._registry.items())


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
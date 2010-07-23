from itertools import izip
from django.contrib.auth.models import User
from django.db.models import OneToOneField, ForeignKey, ManyToManyField
from django.core.exceptions import ObjectDoesNotExist


def _get_rel_fields(opts, types):
	if ManyToManyField in types:
		return opts.fields + opts.many_to_many
	
	return opts.fields


def _get_rel(parent_model, model, related_name=None, types=(ForeignKey,)):
	opts = model._meta
	if related_name:
		# FIXME: what if there's no field?
		link = opts.get_field(related_name)
		if not isinstance(link, types) or \
				(link.rel.to != parent_model and
				 link.rel.to not in parent_model._meta.get_parent_list()):
			raise Exception("field '%s' is not a ForeignKey to %s" % (related_name, parent_model))
	else:
		links_to_parent = [
			f for f in _get_rel_fields(opts, types)
			if isinstance(f, types)
			and (f.rel.to == parent_model
				or f.rel.to in parent_model._meta.get_parent_list())
		]
		if len(links_to_parent) == 1:
			link = links_to_parent[0]
		elif len(links_to_parent) == 0:
			raise Exception("%s has no related fields to %s" % (model, parent_model))
		else:
			raise Exception("%s has more than one related field to %s" % (model, parent_model))
	return link


def flat_get_or_create(self, user):
	return self.model._default_manager.get_or_create(user=user)[0]


class ModelProxyMetaclass(type):
	def __new__(cls, name, bases, attrs):
		super_new = super(ModelProxyMetaclass, cls).__new__
		parents = [b for b in bases if isinstance(b, ModelProxyMetaclass)]
		if not parents:
			return super_new(cls, name, bases, attrs)
		
		module = attrs.pop('__module__')
		new_class = super_new(cls, name, bases, {'__module__': module})
		
		if 'model' not in attrs:
			raise AttributeError("Class %s does not define a model attribute." % name)
		
		new_class.model = attrs['model']
		
		if attrs['model'] != User:
			model = attrs['model']
			related_name = attrs.get('related_field_name', None)
			
			new_class.link = link = _get_rel(
				User,
				model,
				related_name = related_name,
				types=(ForeignKey, OneToOneField, ManyToManyField)
			)
			
			if isinstance(link, OneToOneField) or \
					isinstance(link, ForeignKey) and link.unique:
				new_class._get_for_user = classmethod(flat_get_or_create)
			else:
				new_class._get_for_user = model._default_manager.filter
		return new_class


class ModelProxy(object):
	"""
	Subclasses must define a "model" attribute. They can also define a
	"related_field_name" attribute to specify the field on the model which
	relates to Users.
	"""
	__metaclass__ = ModelProxyMetaclass
	related_field_name = 'users'
	
	@classmethod
	def get_for_user(self, user):
		if self.model == User:
			return user
		
		return self._get_for_user(user=user)


class ProxyField(object):
	# rename as PatchField?
	creation_counter = 0
	
	def __init__(self, proxy, field_name):
		"""
		Proxy should be a ModelProxy class.
		"""
		self.proxy = proxy
		self.field_name = field_name
		self.field = proxy.model._meta.get_field(field_name)
		
		self.creation_counter = ProxyField.creation_counter
		ProxyField.creation_counter += 1
	
	def __getattr__(self, name):
		return getattr(self.field, name)
	
	def contribute_to_class(self, cls, name):
		self.name = name
		self.cls = cls
		setattr(cls._meta, name, self)
		cls._meta.add_field_proxy(self)
	
	def get_data_for_result(self, instance):
		return {self.name: getattr(instance, self.field.name)}


class PatchOptions(object):
	def __init__(self, patch):
		self.patch = patch
		self.model_proxies = set()
		self.field_proxies = []
	
	def add_field_proxy(self, field_proxy):
		if field_proxy not in self.field_proxies:
			self.field_proxies.append(field_proxy)
			self.model_proxies.add(field_proxy.proxy)


class PatchMetaclass(type):
	def __new__(cls, name, bases, attrs):
		super_new = super(PatchMetaclass, cls).__new__
		parents = [b for b in bases if isinstance(b, PatchMetaclass)]
		if not parents:
			return super_new(cls, name, bases, attrs)
		
		module = attrs.pop('__module__')
		new_class = super_new(cls, name, bases, {'__module__': module})
		new_class._meta = PatchOptions(new_class)
		
		for obj_name, obj in attrs.items():
			# FIXME: add creation counter? How does Form do it?
			new_class.add_to_class(obj_name, obj)
		
		return new_class
	
	def add_to_class(cls, name, value):
		if hasattr(value, 'contribute_to_class'):
			value.contribute_to_class(cls, name)
		else:
			setattr(cls, name, value)


class Patch(object):
	__metaclass__ = PatchMetaclass
	
	def __init__(self, *args, **kwargs):
		# cribbed in great part from model init.
		args_len = len(args)
		if args_len > len(self._meta.field_proxies):
			raise IndexError("Number of args exceeds number of fields")
		
		field_proxies_iter = iter(self._meta.field_proxies)
		if not kwargs:
			for val, field in izip(args, field_proxies_iter):
				setattr(self, field.name, val)
		else:
			for val, field in izip(args, field_proxies_iter):
				setattr(self, field.name, val)
				kwargs.pop(field.name, None)
		
		for field in field_proxies_iter:
			# note: django has some extra magic here for related fields... do I
			# need that? I think I might not...
			if kwargs:
				try:
					val = kwargs.pop(field.name)
				except KeyError:
					val = field.get_default()
			else:
				val = field.get_default()
		
			setattr(self, field.name, val)
	
	def save(self):
		pass
	save.alters_data = True
	
	@classmethod
	def get_for_user(self, user):
		# only fetch each required model instance once.
		instances = {}
		for model_proxy in self._meta.model_proxies:
			instances[model_proxy] = model_proxy.get_for_user(user)
		
		kwargs = {}
		for proxy in self._meta.field_proxies:
			kwargs.update(proxy.get_data_for_result(instances[proxy.proxy]))
		
		return self(**kwargs)
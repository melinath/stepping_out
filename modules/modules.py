from itertools import izip
from django.db.models.options import get_verbose_name as convert_camelcase
from django.template.defaultfilters import slugify
from django.utils.text import capfirst


class ModuleOptions(object):
	def __init__(self, module):
		self.module = module
		self.model_proxies = set()
		self.field_proxies = []
	
	def add_field_proxy(self, field_proxy):
		if field_proxy not in self.field_proxies:
			self.field_proxies.append(field_proxy)
			self.model_proxies.add(field_proxy.model_proxy)


class ModuleMetaclass(type):
	def __new__(cls, name, bases, attrs):
		super_new = super(ModuleMetaclass, cls).__new__
		parents = [b for b in bases if isinstance(b, ModuleMetaclass)]
		if not parents:
			return super_new(cls, name, bases, attrs)
		
		module = attrs.pop('__module__')
		new_class = super_new(cls, name, bases, {'__module__': module})
		new_class._meta = ModuleOptions(new_class)
		
		for obj_name, obj in attrs.items():
			# FIXME: add creation counter? How does Form do it?
			new_class.add_to_class(obj_name, obj)
		
		
		if 'verbose_name' not in attrs or 'slug' not in attrs:
			default_name = capfirst(convert_camelcase(name))
			if 'verbose_name' not in attrs:
				new_class.verbose_name = default_name
			
			if 'slug' not in attrs:
				new_class.slug = slugify(default_name)
		
		return new_class
	
	def add_to_class(cls, name, value):
		if hasattr(value, 'contribute_to_class'):
			value.contribute_to_class(cls, name)
		else:
			setattr(cls, name, value)


class Module(object):
	__metaclass__ = ModuleMetaclass
	
	@classmethod
	def get_for_user(self, user):
		# only fetch each required model instance once.
		results = {}
		for model_proxy in self._meta.model_proxies:
			results[model_proxy] = model_proxy.get_for_user(user)
		
		kwargs = {}
		#for proxy in self._meta.field_proxies:
		#	kwargs.update({proxy.name: proxy.value_from_result(results[proxy.proxy])})
		
		instance = self(results=results, **kwargs)
		return instance
	
	def __init__(self, user):
		self.model_proxies = {}
		self._save_funcs = set()
		for model_proxy in self._meta.model_proxies:
			self.model_proxies[model_proxy] = model_proxy(user)
		
		for field_proxy in self._meta.field_proxies:
			self._save_funcs.add(
				field_proxy.get_save_func(
					self.model_proxies[field_proxy.model_proxy]
				)
			)
	
	def get_model_proxy_instance(self, model_proxy_class):
		return self.model_proxies[model_proxy_class]
	
	def save(self):
		for func in self._save_funcs:
			func()
	save.alters_data = True
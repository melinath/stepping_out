from django.contrib.auth.models import User
from django import forms


class ProxyValue(object):
	def __init__(self, name, to_name, proxy_field):
		self.name = name
		self.to_name = to_name
		self.proxy_field = proxy_field # need?
		self.model_proxy = proxy_field.model_proxy
	
	def get_user(self, module_instance):
		return module_instance.get_model_proxy_instance(self.model_proxy).user
	
	def get_for_user(self, module_instance):
		return module_instance.get_model_proxy_instance(self.model_proxy).for_user
	
	def __get__(self, module_instance, owner):
		if not module_instance:
			raise NameError("%s '%s' is only available from an instance" % (self.__class__.__name__, self.name))
		return getattr(self.get_for_user(module_instance), self.to_name)
	
	def __set__(self, module_instance, value):
		setattr(self.get_for_user(module_instance), self.to_name, value)


class ProxyField(object):
	creation_counter = 0
	required = True
	
	def __init__(self, model_proxy, field_name=None):
		# Proxy should be a ModelProxy class. field_name is the name of the
		# field on the actual model.
		self.model_proxy = model_proxy
		self.field_name = field_name
		if field_name is not None:
			self.get_field()
		
		self.creation_counter = ProxyField.creation_counter
		ProxyField.creation_counter += 1
	
	#def __getattr__(self, name):
	#	return getattr(self.field, name)
	
	def get_field(self):
		self.field = self.model_proxy.get_field(self.field_name)
	
	def contribute_to_class(self, cls, name):
		self.name = name
		self.cls = cls
		if self.field_name is None:
			self.field_name = name
			self.get_field()
		setattr(cls, name, ProxyValue(name, self.field.name, self))
		cls._meta.add_field_proxy(self)
	
	def _get_val_from_obj(self, module_instance):
		"""
		Return a value suitable for form field instantiation.
		"""
		return getattr(module_instance, self.name)
	
	def save_form_data(self, module_instance, data):
		setattr(module_instance, self.name, data)
	
	def get_model_proxy_instance(self, module_instance):
		return module_instance.get_model_proxy_instance(self.model_proxy)
	
	def get_save_func(self, model_proxy_instance):
		return model_proxy_instance.save
	
	def formfield(self, **kwargs):
		return self.field.formfield(**kwargs)


class ChoiceOfManyValue(ProxyValue):
	def __init__(self, name, backlink_name, proxy_field):
		self.name = name
		self.backlink_name = backlink_name
		self.proxy_field = proxy_field
		self.model_proxy = proxy_field.model_proxy
	
	def get_backlink_manager(self, module_instance):
		return getattr(self.get_user(module_instance), self.backlink_name)
	
	def get_value(self, module_instance):
		return self.proxy_field._apply_limiter(
			self.get_backlink_manager(module_instance).all()
		)
	
	def __get__(self, module_instance, owner):
		if not module_instance:
			raise NameError("%s '%s' is only available from an instance" % (self.__class__.__name__, self.name))
		return self.get_value(module_instance)
		
	def __set__(self, module_instance, value):
		manager = self.get_backlink_manager(module_instance)
		qs = self.get_value(module_instance)
		total = value | qs
		shared = value & qs
		for model in total:
			if model in shared:
				continue
			if model in value:
				manager.add(model)
			else:
				manager.remove(model)


class ChoiceOfManyField(ProxyField):
	readonly = False
	_choices = None
	
	def __init__(self, model_proxy, limit_choices_to=None):
		self.limit_choices_to = limit_choices_to
		self.model_proxy = model_proxy
		self.backlink_name = model_proxy.link.related_query_name()
	
	def _apply_limiter(self, qs):
		if self.limit_choices_to is not None:
			if isinstance(self.limit_choices_to, Q):
				qs = qs.filter(self.limit_choices_to)
			elif isinstance(self.limit_choices_to, dict):
				qs = qs.filter(**self.limit_choices_to)
			else:
				raise TypeError('%s.limit_choices_to must be a dict or Q object' %
					self.__class__)
		return qs
	
	def _get_val_from_obj(self, module_instance):
		return [model.pk for model in getattr(module_instance, self.name)]
	
	def get_choices(self):
		if self._choices is None:
			qs = self.model_proxy.model._default_manager.all()
			self._choices = self._apply_limiter(qs)
		return self._choices
	choices = property(get_choices)
	
	def contribute_to_class(self, cls, name):
		self.name = name
		self.cls = cls
		setattr(cls, name, ChoiceOfManyValue(name, self.backlink_name, self))
		cls._meta.add_field_proxy(self)
	
	def get_save_func(self, model_proxy_instance):
		return model_proxy_instance.user.save
	
	def formfield(self, form_class=forms.models.ModelMultipleChoiceField, **kwargs):
		defaults = {
			'queryset': self.choices,
			'widget': forms.CheckboxSelectMultiple,
			#'required': self.required
		}
		defaults.update(kwargs)
		return form_class(**defaults)
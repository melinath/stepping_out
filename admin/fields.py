from django.contrib.auth.models import User
from django import forms
from stepping_out.auth.forms import RequiredInlineFormSet
from django.forms.models import inlineformset_factory, ModelForm
from django.db.models import Q


class BaseProxyField(object):
	creation_counter = 0
	
	def __init__(self, model_proxy, required=True, editable=True, help_text=None):
		self.creation_counter = ProxyField.creation_counter
		ProxyField.creation_counter += 1
		
		self.model_proxy = model_proxy
		self.required = required
		self.editable = editable
		self.help_text = help_text
	
	def _get_val_from_obj(self, module_instance):
		raise NotImplementedError
	
	def save_form_data(self, module_instance, data):
		setattr(module_instance, self.name, data) # ?
	
	def __cmp__(self, other):
		# Needed because bisect doesn't take a comparison function. cp. django Field
		return cmp(self.creation_counter, other.creation_counter)


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


class ProxyField(BaseProxyField):
	required = True
	
	def __init__(self, model_proxy, required=True,
				editable=True, help_text=None, field_name=None):
		super(ProxyField, self).__init__(model_proxy, required, editable)
		self.field_name = field_name
		if field_name is not None:
			self.get_field()
	
	def get_field(self):
		"""Fetches a model fields from a model_proxy"""
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
		value = value or manager.none()
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


class ChoiceOfManyField(BaseProxyField):
	readonly = False
	_choices = None
	
	def __init__(self, model_proxy, required=True,
				editable=True, help_text=None, limit_choices_to=None):
		super(ChoiceOfManyField, self).__init__(model_proxy, required, editable, help_text)
		self.limit_choices_to = limit_choices_to
		self.model_proxy = model_proxy
		self.backlink_name = model_proxy.link.related_query_name()
	
	def _apply_limiter(self, qs):
		if self.limit_choices_to is not None:
			if isinstance(self.limit_choices_to, Q):
				qs = qs.filter(self.limit_choices_to)
			elif isinstance(self.limit_choices_to, (list, tuple)):
				qs = qs.filter(*self.limit_choices_to)
			elif isinstance(self.limit_choices_to, dict):
				qs = qs.filter(**self.limit_choices_to)
			else:
				raise TypeError('%s.limit_choices_to must be a list, tuple, dict or Q object' %
					self.__class__)
		return qs
	
	def _get_val_from_obj(self, module_instance):
		return [model.pk for model in getattr(module_instance, self.name)]
	
	def get_choices(self):
		if self._choices is not None:
			return self._choices
		
		qs = self.model_proxy.model._default_manager.all()
		return self._apply_limiter(qs)
	choices = property(get_choices)
	
	def contribute_to_class(self, cls, name):
		self.name = name
		self.cls = cls
		setattr(cls, name, ChoiceOfManyValue(name, self.backlink_name, self))
		cls._meta.add_field_proxy(self)
	
	def get_save_func(self, model_proxy_instance):
		return model_proxy_instance.user.save
	
	def formfield(self, form_class=forms.models.ModelMultipleChoiceField, widget=forms.CheckboxSelectMultiple, **kwargs):
		defaults = {
			'queryset': self.choices,
			'widget': widget,
			'required': self.required,
			#'readonly': not self.editable How does django admin do this?
		}
		defaults.update(kwargs)
		return form_class(**defaults)


class InlineProxyValue(ProxyValue):
	def __init__(self, name, backlink_name, proxy_field):
		self.name = name
		self.backlink_name = backlink_name
		self.proxy_field = proxy_field
		self.model_proxy = proxy_field.model_proxy
	
	def get_backlink_manager(self, module_instance):
		return getattr(self.get_user(module_instance), self.backlink_name)
	
	def __get__(self, module_instance, owner):
		return self.get_backlink_manager(module_instance).all()
	
	def __set__(self, module_instance, value):
		raise NotImplementedError


class InlineField(BaseProxyField):
	def __init__(self, model_proxy, required=True, editable=True, help_text=None,
			fields=None, exclude=None, extra=3, fieldsets=None,
			formset=RequiredInlineFormSet, form=ModelForm):
		super(InlineField, self).__init__(model_proxy, required, editable, help_text)
		self.fields = fields
		self.exclude = exclude
		self.extra = extra
		self.backlink_name = model_proxy.link.related_query_name()
		self.formset_class = formset
		self.form_class = form
		self.formset = self.get_formset()
		self.formset.help_text = self.help_text
	
	def get_formset(self):
		formset = inlineformset_factory(User, self.model_proxy.model,
			fields=self.fields, exclude=self.exclude, extra=self.extra,
			formset=self.formset_class, form=self.form_class)
		formset.required = self.required
		return formset
	
	def contribute_to_class(self, cls, name):
		self.name = name
		self.cls = cls
		setattr(cls, name, InlineProxyValue(name, self.backlink_name, self))
		cls._meta.add_field_proxy(self)
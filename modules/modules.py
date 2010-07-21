from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.options import get_verbose_name as convert_camelcase
from django.forms.models import ModelMultipleChoiceField
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict


__all__ = (
	'FieldSet', 'Module', 'InlineModule', 'ModuleModel', 'ModuleInlineModel',
	'ModuleMultiModel'
)


class FieldSet(object):
	def __init__(self, title, opts, form):
		self.title = title
		self.fields = opts['fields']
		self.form = form
	
	def __iter__(self):
		for field in self.fields:
			yield self.form[field]


class Module(object):
	"""
	A module defines a collection of ModuleModels and the fieldsets (declared
	as in django's ModelAdmin class) used to display the related fields.
	"""
	fieldsets = None
	
	@classmethod
	def _get_fieldsets(self, fieldsets, form):
		return [FieldSet(title, opts, form) for title, opts in fieldsets]
	
	@classmethod
	def get_fieldsets(self, form):
		if self.fieldsets is not None:
			fieldsets = self.fieldsets
		else:
			fieldsets = ((None, {'fields': self.get_fields()}),)
		
		return self._get_fieldsets(fieldsets, form)
	
	@classmethod
	def get_fields(self):
		all_fields = []
		for model in self.models:
			if hasattr(model, 'fields'):
				all_fields.extend(model.fields)
			elif hasattr(model, 'field_name'):
				all_fields.append(model.field_name)
		return all_fields

class InlineModule(Module):
	@classmethod
	def get_fieldsets(self, formset):
		if self.fieldsets is not None:
			fieldsets = self.fieldsets
		else:
			fieldsets = ((None, {'fields': self.get_fields()}),)
		
		FieldSets = []
		for form in formset:
			FieldSets.extend(self._get_fieldsets(fieldsets, form))
		
		return FieldSets
	

class BaseModuleModel(object):
	"""
	ModuleModels, ModuleChoiceModels, and ModuleInlineModels present a common
	interface between a stepping_out Module and a django Model class. Most
	importantly, a modulemodel must be able to return a model or collection of
	models related to a django.contrib.auth User instance.
	"""
	def get_for_user(self, user):
		if not isinstance(user, User):
			return None
		
		return self._get_for_user(user)
	
	@property
	def slug(self):
		# is this necessary?
		return slugify(convert_camelcase(self.__class__.__name__))
	
	def __iadd__(self, other):
		if self.__class__ != other.__class__:
			raise TypeError("unsupported operand type(s) for +=: '%s' and '%s'" %
				(self.__class__.__name__, other.__class__.__name__))


class ModuleModel(BaseModuleModel):
	"""
	Subclasses may override the `related_field` attribute to specify a different
	field on the model which relates to a User instance.
	"""
	related_field = 'user'
	
	def __init__(self, fields):
		self.fields = fields
	
	def _get_for_user(self, user):
		kwargs = {self.related_field: user}
		return self.model._default_manager.get(**kwargs)
	
	def __iadd__(self, other):
		super(ModuleModel, self).__iadd__(other)
		self.fields += other.fields
		return self


class ModuleInlineModel(ModuleModel):
	def _get_for_user(self, user):
		kwargs = {self.related_field: user}
		return self.model._default_manager.filter(**kwargs)


class ModuleMultiModel(BaseModuleModel):
	"""
	Subclasses may override the `related_field` attribute to specify a field on
	the	model which relates to a User instance.
	
	Subclasses may be initialized with a kwarg dict or Q object to restrict the
	queryset further.
	"""
	related_field = 'users'
	field_class = ModelMultipleChoiceField
	required = False
	
	def __init__(self, field_name, limit_choices_to=None):
		self.limit_choices_to = limit_choices_to
		self.field_name = field_name
	
	def _get_for_user(self, user):
		kwargs = {self.related_field: user}
		return self.queryset.filter(**kwargs)
	
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
	
	def _get_queryset(self):
		if not hasattr(self, '_queryset'):
			qs = self.model._default_manager.all()
			self._queryset = self._apply_limiter(qs)
		
		return self._queryset
	queryset = property(_get_queryset)
	
	def __iadd__(self, other):
		super(ModuleMultiModel, self).__iadd__(other)
		self._queryset = self.queryset | other.queryset
		return self
	
	@property
	def related_manager_attr_name(self):
		return self.model._meta.get_field(self.related_field).related_query_name()
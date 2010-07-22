from django.contrib.auth.models import User
from django.db.models import OneToOneField, ForeignKey, ManyToManyField
from django.db.models.options import get_verbose_name as convert_camelcase
from django.forms.models import _get_foreign_key, modelform_factory, inlineformset_factory
from django.template.defaultfilters import slugify


#from django.utils.datastructures import SortedDict
#from django.db.models import Q
from django.forms.models import ModelMultipleChoiceField

"""
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
"""


def _get_rel(parent_model, model, related_name, types=(ForeignKey,)):
	opts = model._meta
	if related_name:
		# FIXME: what if there's no field?
		link = opts.get_field(related_name)
		if not isinstance(link, types) or \
				(field.rel.to != parent_model and
				 field.rel.to not in parent_model._meta.get_parent_list()):
			raise Exception("field '%s' is not a ForeignKey to %s" % (related_name, parent_model))
	else:
		links_to_parent = [
            f for f in opts.fields
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

"""
def get_segment_class(model, related_name):
	link = _get_rel(User, model, related_name)
	
	if isinstance(link, OneToOneField) or \
		isinstance(link, ForeignKey) and link.unique:
		return Segment
	elif isinstance(link, ForeignKey):
		return ForeignKeySegment
	else:
		return ManyToManySegment
"""


class Segment(object):
	model = None
	related_field = 'users'
	
	def contribute_to_module(self, module):
		self.module = module


class OneToOneSegment(Segment):
	def __init__(self, fields):
		self.fields = fields
		self.form = modelform_factory(self.model)
		#super(OneToOneSegment, self).__init__(fields)
	
	def get_forms(self, request):
		kwargs = {self.related_field: request.user} 
		self.instance = self.model._default_manager.get(**kwargs)
		if request.method == 'POST':
			return [self.form(request.POST, request.FILES, instance=self.instance)]
		else:
			return [self.form(instance=self.instance)]


class ForeignKeySegment(Segment):
	fieldsets = None
	
	def __init__(self, fields):
		self.fields = fields
		self.formset = inlineformset_factory(User, self.model)
	
	def get_forms(self, request):
		if request.method == 'POST':
			return self.formset(request.POST, request.FILES, instance=request.user).forms
		else:
			return self.formset(instance=request.user).forms


class ManyToManySegment(Segment):
	def __init__(self, limit_choices_to=None):
		self.limit_choices_to = limit_choices_to
		m2m = _get_rel(User, self.model, types=(ManyToManyField,))
		self.backlink = m2m.name
		self.form = modelform_factory(User, fields=[m2m.name])
	
	def get_forms(self, request):
		if request.method == 'POST':
			return [self.form(request.POST, request.FILES, instance=request.user)]
		else:
			return [self.formset(instance=requests.user)]


class Module(object):
	fieldsets = None
	segments = []
	
	@classmethod
	def get_forms(self, request):
		forms = []
		for segment in self.segments:
			forms.extend(segment.get_forms(request))
		return forms
	
	@classmethod
	def get_fieldsets(self):
		pass


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

"""
class BaseModuleModel(object):
	""
	ModuleModels, ModuleChoiceModels, and ModuleInlineModels present a common
	interface between a stepping_out Module and a django Model class. Most
	importantly, a modulemodel must be able to return a model or collection of
	models related to a django.contrib.auth User instance.
	""
	def get_for_user(self, user):
		if not isinstance(user, User):
			return None
		
		return self._get_for_user(user)
	
	@property
	def slug(self):
		# is this necessary?
		return slugify(convert_camelcase(self.__class__.__name__))


class ModuleModel(BaseModuleModel):
	""
	Subclasses may override the `related_field` attribute to specify a different
	field on the model which relates to a User instance.
	""
	related_field = 'user'
	
	def __init__(self, fields):
		self.fields = fields
	
	def _get_for_user(self, user):
		kwargs = {self.related_field: user}
		return self.model._default_manager.get(**kwargs)


class ModuleInlineModel(ModuleModel):
	def _get_for_user(self, user):
		kwargs = {self.related_field: user}
		return self.model._default_manager.filter(**kwargs)


class ModuleMultiModel(BaseModuleModel):
	""
	Subclasses may override the `related_field` attribute to specify a field on
	the	model which relates to a User instance.
	
	Subclasses may be initialized with a kwarg dict or Q object to restrict the
	queryset further.
	""
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
"""
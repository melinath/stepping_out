from django.contrib.admin.util import flatten_fieldsets
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.options import get_verbose_name as convert_camelcase
from django.forms import Form
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict
from django.utils.text import capfirst


import pdb


class ModuleFieldSet(object):
	def __init__(self, title, opts, form):
		self.title = title
		self.fields = opts['fields']
		self.form = form
	
	def __iter__(self):
		for field in self.fields:
			yield self.form[field]


class ModuleModelMetaclass(type):
	def __new__(cls, name, bases, attrs):
		super_new = super(ModuleModelMetaclass, cls).__new__
		parents = [b for b in bases if isinstance(b, ModuleModelMetaclass)]
		if not parents:
			return super_new(cls, name, bases, attrs)
		
		if bases and 'model' not in attrs:
			raise AttributeError("%s must relate to a model.")
		
		return super_new(cls, name, bases, attrs)


# FIXME: Better class name.
# FIXME: Should ModuleModel deal with auth questions?
class ModuleModel(object):
	"""
	This class defines an interface between a Module and a Model - specifically,
	how to return a model related to a given django.contrib.auth.User instance.
	
	Subclasses may define a `related_field` attribute to specify a field on the
	model which relates to a User instance. ('user' will be checked if no
	related_field is specified.
	"""
	__metaclass__ = ModuleModelMetaclass
	
	def __init__(self, user):
		self.user = user
	
	def _get_for_user(self, user):
		kwargs = {getattr(self, 'related_field', 'user'): user}
		return self.model._default_manager.get(**kwargs)
	
	def get_instance(self):
		if not isinstance(self.user, User):
			return None
		
		return self._get_for_user(self.user)


class ModuleMetaclass(type):
	def __new__(cls, name, bases, attrs):
		declared_models = attrs.get('models', [])
		attrs['models'] = SortedDict(
			[(model, set(fields)) for model, fields in declared_models]
		)
		return super(ModuleMetaclass, cls).__new__(cls, name, bases, attrs)


class Module(object):
	"""
	A module is essentially a mapping of ModuleModels to fields. It also allows
	the definition of FieldSets in the style of the Django default admin.
	"""
	__metaclass__ = ModuleMetaclass
	fieldsets = None
	
	@classmethod
	def get_fieldsets(self):
		if self.fieldsets:
			return self.fieldsets
		return ((None, {'fields': self.get_fields()}),)
	
	@classmethod
	def get_fields(self):
		all_fields = []
		for fields in self.models.values():
			all_fields.extend(list(fields))
		return all_fields


def process_modules(modules):
	models = SortedDict()
	forms = []
	base_fields = SortedDict()
	
	for module in modules:
		for model, fields in module.models.items():
			if not issubclass(model, ModuleModel):
				raise TypeError('%s must subclass %s.ModuleModel' % 
					(model, self.__module__))
			
			if model not in models:
				models[model] = set()
			
			models[model] |= set(fields)
	
	for model, fields in models.items():
		form = modelform_factory(model.model, fields=list(fields))
		forms.append(form)
		base_fields.update(form.base_fields)
	
	return forms, base_fields, models


class SectionMetaclass(Form.__metaclass__):
	"""
	This metaclass creates base fields according to a section's modules and sets
	a few default items on a class if they weren't defined already.
	"""
	def __new__(cls, name, bases, attrs):
		super_new = super(Form.__metaclass__, cls).__new__
		parents = [b for b in bases if isinstance(b, SectionMetaclass)]
		if not parents:
			return super_new(cls, name, bases, attrs)
		
		subforms, base_fields, models = process_modules(attrs['modules'])
		attrs.update({
			'subforms': subforms,
			'base_fields': base_fields,
			'models': models
		})
		
		default_name = capfirst(convert_camelcase(name))
		if 'title' not in attrs:
			attrs['title'] = default_name
		
		if 'slug' not in attrs:
			attrs['slug'] = slugify(default_name)
		
		return super_new(cls, name, bases, attrs)


class Section(Form):
	"""
	A section is a collection of modules. It subclasses Form, but pulls its
	base_fields from section.modules instead of direct declaration.
	
	A subclass must define:
	section.modules
	
	A subclass may define:
	section.title
	section.slug
	section.template
	section.help_text
	"""
	__metaclass__ = SectionMetaclass
	template = 'stepping_out/modules/section.html'
	
	def __init__(self, admin_site):
		self.admin_site = admin_site
	
	def __call__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		return self
	
	def __iter__(self):
		return self.fieldsets.__iter__()
	
	def get_context(self, **kwargs):
		defaults = {
			'sections': self.admin_site.sections
		}
		defaults.update(kwargs)
		return defaults
	
	def get_fieldsets(self):
		if not hasattr(self, '_fieldsets'):
			fieldsets = []
			for module in self.modules:
				for title, opts in module.get_fieldsets():
					fieldsets.append(ModuleFieldSet(title, opts, self))
			self._fieldsets = fieldsets
		
		return self._fieldsets
	fieldsets = property(get_fieldsets)
	
	def has_permission(self, request):
		if request.user.is_active and request.user.is_authenticated():
			return True
		
		return False
	
	def view(self, request):
		if request.method == 'POST':
			valid = []
			invalid = []
			
			for model, form_klass in zip(self.models, self.subforms):
				form = form_klass(
					request.POST,
					request.FILES,
					instance=model(request.user).get_instance()
				)
				if form.is_valid():
					valid.append(form)
				else:
					invalid.append(form)
			
			if not invalid:
				for form in valid:
					form.save()
				return HttpResponseRedirect('')
			
			form = self(request.POST, request.FILES)
		else:
			# need to set initial data from the db.
			initial = {}
			for model, form_klass in zip(self.models, self.subforms):
				form = form_klass(instance=model(request.user).get_instance())
				initial.update(form.initial)
			form = self(initial=initial)
		
		context = self.get_context(
			form=form
		)
		
		template = self.template
		context_instance = RequestContext(request)
		return render_to_response(
			template,
			context,
			context_instance=context_instance
		)
	
	def get_urls(self):
		from django.conf.urls.defaults import patterns, url
		
		def wrap(view):
			def inner(request, *args, **kwargs):
				if not self.has_permission(request):
					return self.admin_site.login(request, *args, **kwargs)
				return view(request, *args, **kwargs)
			return inner
		
		urlpatterns = patterns('',
			url(r'^$', wrap(self.view),
				name='%s_%s' % (self.admin_site.url_prefix, self.slug)),
		)
		return urlpatterns
	urls = property(get_urls)
	
	def get_absolute_url(self):
		return reverse('%s_%s' % (self.admin_site.url_prefix, self.slug))
	absolute_url = property(get_absolute_url)
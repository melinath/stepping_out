from django.core.urlresolvers import reverse
from django.db.models.options import get_verbose_name as convert_camelcase
from django.forms import Form, CheckboxSelectMultiple
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict
from django.utils.text import capfirst
from stepping_out.modules.modules import ModuleModel, ModuleMultiModel


class FieldSet(object):
	def __init__(self, title, opts, form):
		self.title = title
		self.fields = opts['fields']
		self.form = form
	
	def __iter__(self):
		for field in self.fields:
			yield self.form[field]


class SectionSub(object):
	"""
	Sectionsubs interpret ModuleModels in order to validate, pull, and save form
	data. On the way, they should provide a `base_fields` dictionary of
	<field_attr_name>: <form_field> to be added to a section's base_fields.
	"""
	def __init__(self, model):
		self.model = model


class SectionSubForm(SectionSub):
	def __init__(self, model):
		self.form_class = modelform_factory(
			model.model,
			fields=list(model.fields)
		)
		self.form = None
		super(SectionSubForm, self).__init__(model)
	
	@property
	def base_fields(self):
		return self.form_class.base_fields
	
	@property
	def initial(self):
		if self.form is None:
			raise TypeError("SectionSubForm must be instantiated before its initial values are available.")
		return self.form.initial
	
	def instantiate(self, request):
		if request.method == 'POST':
			self.form = self.form_class(
				request.POST,
				request.FILES,
				instance=self.model.get_for_user(request.user)
			)
		else:
			self.form = self.form_class(instance=self.model.get_for_user(request.user))
	
	def is_valid(self):
		return self.form.is_valid()
	
	def save(self, *args, **kwargs):
		self.form.save(*args, **kwargs)


class SectionSubInline(SectionSub):
	pass


class SectionSubField(SectionSub):
	def __init__(self, model):
		self.field =  model.field_class(
			queryset = model.queryset,
			widget = CheckboxSelectMultiple,
			required = model.required
		)
		super(SectionSubField, self).__init__(model)
	
	def instantiate(self, request):
		self.user = request.user
		if request.method == 'POST':
			self.value = self.field.widget.value_from_datadict(
				request.POST,
				request.FILES,
				self.model.field_name
			)
	
	@property
	def base_fields(self):
		return {self.model.field_name: self.field}
	
	@property
	def initial(self):
		initial = {
			self.model.field_name: [model.pk for model in self.model.get_for_user(self.user)]
		}
		return initial
	
	def is_valid(self):
		# FIXME: record the error messages for later display.
		try:
			self.field.validate(self.value)
		except:
			return False
		
		return True
	
	def save(self, *args, **kwargs):
		qs = self.field.clean(self.value)
		manager = getattr(self.user, self.model.related_manager_attr_name)
		manager.clear()
		for model in qs:
			manager.add(model)
		
		self.user.save()


def process_modules(modules):
	"""
	There are a couple things that are needed to make everything work.
	1. models - actually ModuleModels. These are used by subs for database
	   interaction. Don't need to be returned.
	2. subs - Used for data validation. Use ModelForms or other means to pull
	   and push database data for a given modulemodel.
	3. base_fields - for building the form correctly and for passing to FieldSets.
	4. fieldsets
	"""
	models = {}
	subs = []
	base_fields = SortedDict()
	#inline_models = SortedDict()
	#inline_formsets = []
	
	for module in modules:
		for model in module.models:
			if not isinstance(model, ModuleModel) and not isinstance(model, ModuleMultiModel):
				raise TypeError('%s must subclass ModuleModel or ModuleMultiModel' % 
					(model, self.__module__))
			
			if model.__class__ not in models:
				models[model.__class__] = model
			else:
				models[model.__class__] += model
	
	for model in models.values():
		if isinstance(model, ModuleModel):
			sub = SectionSubForm
		#elif fields:
		#	sub = SectionSubInline
		else:
			sub = SectionSubField
		sub = sub(model)
		subs.append(sub)
		base_fields.update(sub.base_fields)
	
	return subs, base_fields


class SectionMetaclass(Form.__metaclass__):
	"""
	This metaclass creates base fields according to a section's modules and sets
	a few default items on a class if they weren't defined already.
	"""
	def __new__(cls, name, bases, attrs):
		new_cls = super(SectionMetaclass, cls).__new__(cls, name, bases, attrs)
		parents = [b for b in bases if isinstance(b, SectionMetaclass)]
		if not parents:
			return new_cls
		
		new_cls.subs, new_cls.base_fields = process_modules(new_cls.modules)
		
		default_name = capfirst(convert_camelcase(name))
		if 'title' not in attrs:
			new_cls.title = default_name
		
		if 'slug' not in attrs:
			new_cls.slug = slugify(default_name)
		
		return new_cls


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
					fieldsets.append(FieldSet(title, opts, self))
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
			
			for sub in self.subs:
				sub.instantiate(request)
				if sub.is_valid():
					valid.append(sub)
				else:
					invalid.append(sub)
			
			if not invalid:
				for sub in valid:
					sub.save()
				return HttpResponseRedirect('')
			
			form = self(request.POST, request.FILES)
		else:
			# need to set initial data from the db.
			initial = {}
			for sub in self.subs:
				sub.instantiate(request)
				initial.update(sub.initial)
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
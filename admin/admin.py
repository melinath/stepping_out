from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from stepping_out.admin import moduleform_factory
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.widgets import SelectMultiple


class FieldSet(object):
	def __init__(self, form, title, opts):
		self.form = form
		self.title = title
		self.fields = opts['fields']
	
	def __iter__(self):
		for field in self.fields:
			try:
				yield self.form.formset_instances[field]
			except KeyError:
				yield self.form[field]


class ModuleAdmin(object):
	verbose_name = None
	slug = None
	help_text = None
	order = None
	form_class = None
	template = 'stepping_out/modules/module.html'
	fieldsets = None
	
	def __init__(self, admin_site, module_class):
		self.admin_site = admin_site
		self.module_class = module_class
		if self.verbose_name is None:
			self.verbose_name = module_class.verbose_name
		
		if self.slug is None:
			self.slug = module_class.slug
		
		if self.form_class is None:
			self.form_class = moduleform_factory(module_class)
	
	@property
	def urls(self):
		def wrap(view, cacheable=False):
			return self.admin_view(view, cacheable)
		
		urlpatterns = patterns('',
			url(r'^$', wrap(self.base_view),
				name='%s_%s' % (self.admin_site.url_prefix, self.slug)),
		)
		return urlpatterns
	
	def get_root_url(self):
		return reverse('%s_%s' % (self.admin_site.url_prefix, self.slug))
	
	def get_subnav(self):
		return None
	subnav = property(get_subnav)
	
	def get_fieldsets(self, form):
		if self.fieldsets is not None:
			fieldsets = []
			for title, opts in self.fieldsets:
				fieldsets.append(FieldSet(form, title, opts))
			return fieldsets
		
		return [FieldSet(form, None, {'fields': form.all_fields.keys()})]
	
	def get_context(self, request):
		context = self.admin_site.get_context(request)
		context.update({
			'admin': self
		})
		return context
	
	def has_permission(self, request):
		if request.user.is_active and request.user.is_authenticated():
			return True
		
		return False
	
	def admin_view(self, view, cacheable=False, test=None):
		def inner(request, *args, **kwargs):
			if not self.has_permission(request):
				raise Http404
			return view(request, *args, **kwargs)
		return self.admin_site.admin_view(inner)
	
	def redirect(self):
		"""
		For some reason, if this is not included as a method, django can't find
		HttpResponseRedirect...
		"""
		return HttpResponseRedirect('')
	
	def add_messages(self, request, msgs):
		for level, msg in msgs:
			messages.add_message(request, level, msg, fail_silently=False)
	
	def base_view(self, request):
		module = self.module_class(request.user)
		form_class = self.form_class
		
		if request.method == 'POST':
			form = form_class(module, request.POST, request.FILES)
			
			if form.is_valid():
				form.save()
				self.add_messages(request, form.messages)
				return self.redirect()
		else:
			form = form_class(module)
		
		fieldsets = self.get_fieldsets(form)
		context = self.get_context(request)
		context.update({
			'form': form,
			'fieldsets': fieldsets
		})
		template = self.template
		context_instance = RequestContext(request)
		
		return render_to_response(
			template,
			context,
			context_instance=context_instance
		)


class ConfigurationModuleAdmin(ModuleAdmin):
	base_template = 'stepping_out/modules/config/base.html'
	create_template = 'stepping_out/modules/config/create.html'
	edit_template = 'stepping_out/modules/config/edit.html'
	create_form = None
	edit_form = None
	
	def __init__(self, admin_site, module_class):
		self.admin_site = admin_site
		self.module_class = module_class
		
		if self.verbose_name is None:
			self.verbose_name = module_class.verbose_name
		
		if self.slug is None:
			self.slug = module_class.slug
		
		if self.create_form is None:
			self.create_form = self.default_form
		
		if self.edit_form is None:
			self.edit_form = self.default_form
	
	@property
	def default_form(self):
		if not hasattr(self, '_default_form'):
			form = modelform_factory(self.module_class.model)
			for name, field in form.base_fields.items():
				if isinstance(field.widget, SelectMultiple):
					field.widget = FilteredSelectMultiple(name.replace('_', ' '), False)
			self._default_form = form
		return self._default_form
	
	def has_permission(self, request):
		return request.user.has_perm('change', self.module_class.model)
	
	@property
	def urls(self):
		def wrap(view, cacheable=False):
			return self.admin_view(view, cacheable)
		
		urlpatterns = patterns('',
			url(r'^$', wrap(self.base_view), name="%s_%s_root" % (self.admin_site.url_prefix, self.slug)),
			url(r'^create/$', wrap(self.create_view), name="%s_%s_create" % (self.admin_site.url_prefix, self.slug)),
			url(r'^(?P<object_id>\d+)/$', wrap(self.edit_view), name="%s_%s_edit" % (self.admin_site.url_prefix, self.slug))
		)
		return urlpatterns
	
	def get_root_url(self):
		return reverse('%s_%s_root' % (self.admin_site.url_prefix, self.slug))
	
	def get_subnav(self):
		subnav = (
			(reverse('%s_%s_create' % (self.admin_site.url_prefix, self.slug)), 'Create'),
		)
		for instance in self.module_class.get_queryset():
			subnav += (
				(reverse('%s_%s_edit' % (self.admin_site.url_prefix, self.slug), kwargs={'object_id': instance.id}), unicode(instance)),
			)
		return subnav
	subnav = property(get_subnav)
	
	def base_view(self, request):
		return render_to_response(self.base_template, self.get_context(request),
			context_instance=RequestContext(request))
	
	def create_view(self, request):
		if request.method == 'POST':
			form = self.create_form(request.POST)
			if form.is_valid():
				obj = form.save()
				return HttpResponseRedirect(reverse(self.edit_view, kwargs={'object_id': obj.id}))
		else:
			form = self.create_form()
		context = self.get_context(request)
		context.update({'form': form})
		return render_to_response(self.create_template, context, context_instance=RequestContext(request))
	
	def edit_view(self, request, object_id):
		instance = get_object_or_404(self.module_class.model, id=object_id)
		
		if request.method == 'POST':
			form = self.edit_form(request.POST, instance=instance)
			if form.is_valid():
				obj = form.save()
				messages.add_message(request, messages.SUCCESS, 'Changes made successfully.')
		else:
			form = self.edit_form(instance=instance)
		
		context = self.get_context(request)
		context.update({'form': form})
		
		return render_to_response(self.edit_template, context, context_instance=RequestContext(request))
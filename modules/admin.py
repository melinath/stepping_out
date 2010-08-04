from django.core.urlresolvers import reverse
from stepping_out.modules import moduleform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages


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
		from django.conf.urls.defaults import patterns, url
		
		def wrap(view, cacheable=False):
			return self.admin_site.admin_view(view, cacheable)
		
		urlpatterns = patterns('',
			url(r'^$', wrap(self.view),
				name='%s_%s' % (self.admin_site.url_prefix, self.slug)),
		)
		return urlpatterns
	
	def get_absolute_url(self):
		return reverse('%s_%s' % (self.admin_site.url_prefix, self.slug))
	absolute_url = property(get_absolute_url)
	
	def get_fieldsets(self, form):
		if self.fieldsets is not None:
			fieldsets = []
			for title, opts in self.fieldsets:
				fieldsets.append(FieldSet(form, title, opts))
			return fieldsets
		
		return [FieldSet(form, None, {'fields': form.all_fields.keys()})]
	
	def get_context(self):
		context = self.admin_site.get_context()
		context.update({
			'admin': self
		})
		# here's where I would add fieldsets?
		return context
	
	def has_permission(self, request):
		if request.user.is_active and request.user.is_authenticated():
			return True
		
		return False
	
	def redirect(self):
		"""
		For some reason, if this is not included as a method, django can't find
		HttpResponseRedirect...
		"""
		return HttpResponseRedirect('')
	
	def add_messages(self, request, msgs):
		for level, msg in msgs:
			messages.add_message(request, level, msg, fail_silently=False)
	
	def view(self, request):
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
		context = self.get_context()
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
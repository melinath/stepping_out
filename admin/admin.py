from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.forms.widgets import SelectMultiple
from stepping_out.admin.datastructures import OrderedDict


class AdminSection(object):
	"""
	This is a base class for all admin sections. Should be subclassed to provide
	section-specific functionality.
	"""
	verbose_name = None
	slug = None
	help_text = None
	order = None
	template = 'stepping_out/admin/sections/basic.html'
	form = None
	
	def __init__(self, admin_site):
		self.admin_site = admin_site
	
	@property
	def urls(self):
		def wrap(view, cacheable=False):
			return self.admin_view(view, cacheable)
		
		urlpatterns = patterns('',
			url(r'^$', wrap(self.basic_view),
				name='%s_%s' % (self.admin_site.url_prefix, self.slug)),
		)
		return urlpatterns
	
	def get_root_url(self):
		return reverse('%s_%s' % (self.admin_site.url_prefix, self.slug))
	
	def get_nav(self, request):
		if self.has_permission(request):
			url = self.get_root_url()
			return [{
				'title': self.verbose_name,
				'url': self.get_root_url(),
				'selected': self.is_selected(request),
			}]
		return []
	
	def is_selected(self, request):
		if request.path == self.get_root_url():
			return True
		return False
	
	def get_context(self):
		return {
			'admin': self
		}
	
	def has_permission(self, request):
		return request.user.is_active and request.user.is_authenticated()
	
	def admin_view(self, view, cacheable=False, test=None):
		def inner(request, *args, **kwargs):
			if not self.has_permission(request):
				raise Http404
			return view(request, *args, **kwargs)
		return self.admin_site.admin_view(inner)
	
	def basic_view(self, request, extra_context=None):
		context = self.get_context()
		context.update(extra_context or {})
		context.update({'navbar': self.admin_site.get_nav(request)})
		template = self.template
		
		return render_to_response(
			template,
			context,
			context_instance=RequestContext(request)
		)


class FormAdminSection(AdminSection):
	form = None
	
	def basic_view(self, request, extra_context=None):
		if self.form is not None:
			if request.method == 'POST':
				form = self.form(request.POST, request.FILES)
				
				if form.is_valid():
					form.save()
					return HttpResponseRedirect('')
			else:
				form = self.form()
			
			extra_context = extra_context or {}
			extra_context.update({
				'form': form
			})
		return super(FormAdminSection, self).basic_view(request, extra_context)


class QuerySetAdminSection(AdminSection):
	base_template = 'stepping_out/admin/sections/queryset/base.html'
	create_template = 'stepping_out/admin/sections/queryset/create.html'
	edit_template = 'stepping_out/admin/sections/queryset/edit.html'
	create_form = None
	edit_form = None
	model = None
	
	def __init__(self, admin_site):
		if self.create_form is None:
			self.create_form = self.get_default_form()
		
		if self.edit_form is None:
			self.edit_form = self.get_default_form()
	
	def get_default_form(self):
		return modelform_factory(self.model)
	
	def has_permission(self, request):
		opts = self.model._meta
		return request.user.is_authenticated() and (request.user.has_perm('%s.%s' % (opts.app_label, opts.get_add_permission())) or request.user.has_perm('%s.%s' % (opts.app_label, opts.get_change_permission())))
	
	@property
	def urls(self):
		def wrap(view, perm=None, cacheable=False):
			ct = ContentType.objects.get_for_model(self.module_class.model)
			def inner(request, *args, **kwargs):
				if perm is not None and not request.user.has_perm('%s.%s_%s' % (ct.app_label, perm, ct.model)):
					raise Http404
				return view(request, *args, **kwargs)
			inner = self.admin_view(inner)
			return inner
		opts = self.model._meta
		urlpatterns = patterns('',
			url(r'^$', wrap(self.basic_view), name="%s_%s_root" % (self.admin_site.url_prefix, self.slug)),
			url(r'^create/$', wrap(self.create_view, '%s.%s' % (opts.app_label, opts.get_add_permission())), name="%s_%s_create" % (self.admin_site.url_prefix, self.slug)),
			url(r'^(?P<object_id>\d+)/edit/$', wrap(self.edit_view, '%s.%s' % (opts.app_label, opts.get_change_permission())), name="%s_%s_edit" % (self.admin_site.url_prefix, self.slug))
		)
		return urlpatterns
	
	def get_root_url(self):
		return reverse('%s_%s_root' % (self.admin_site.url_prefix, self.slug))
	
	def get_queryset(self):
		return self.model.all()
	
	def get_nav(self, request):
		if self.has_permission(request):
			main_is_active = False
			children = []
			info = self.admin_site.url_prefix, self.slug
			
			opts = self.model._meta
			
			if request.user.has_perm('%s.%s' % (opts.app_label, opts.get_add_permission())):
				url = reverse('%s_%s_create' % info)
				is_active = (url == request.path)
				if is_active:
					main_is_active = True
				children.append({
					'url': url,
					'title': 'Create',
					'selected': is_active,
				})
			
			if request.user.has_perm('%s.%s' % (opts.app_label, opts.get_change_permission())):
				edit_children = []
				edit_is_active = False
				for instance in self.get_queryset():
					url = reverse('%s_%s_edit' % info, kwargs={'object_id': instance.id})
					is_active = (url == request.path)
					if is_active:
						edit_is_active = True
					edit_children.append({
						'title': unicode(instance),
						'url': url,
						'selected': is_active,
					})
				
				if edit_is_active:
					main_is_active = True
				children.append({
					'title': 'Edit',
					'url': None,
					'selected': edit_is_active,
					'children': edit_children,
				})
			return [{
				'title': self.verbose_name,
				'url': None,
				'selected': main_is_active,
				'children': children,
			}]
		return []
	
	def basic_view(self, request, extra_context=None):
		context = extra_context or {}
		context.update({'list': self.model.objects.all()})
		return self.create_view(template=self.base_template)
	
	def create_view(self, request, extra_context=None, template=None):
		if request.method == 'POST':
			form = self.create_form(request, request.POST, request.FILES)
			if form.is_valid():
				obj = form.save()
				messages.add_message(request, messages.SUCCESS, 'Object added successfully. You may continue editing it below.')
				return HttpResponseRedirect(reverse('%s_%s_edit' % (self.admin_site.url_prefix, self.slug), kwargs={'object_id': obj.id}))
		else:
			form = self.create_form(request)
		
		if template is None:
			template = self.create_template
		
		context = self.get_context()
		context.update(extra_context or {})
		context.update({'form': form})
		return render_to_response(template, context,
			context_instance=RequestContext(request))
	
	def edit_view(self, request, object_id, extra_context=None):
		instance = get_object_or_404(self.model, id=object_id)
		
		if request.method == 'POST':
			form = self.edit_form(request, request.POST, request.FILES, instance=instance)
			if form.is_valid():
				obj = form.save()
				messages.add_message(request, messages.SUCCESS, 'Changes made successfully.')
				return HttpResponseRedirect('')
		else:
			form = self.edit_form(request, instance=instance)
		
		context = self.get_context()
		context.update(extra_context or {})
		context.update({'form': form})
		return render_to_response(self.edit_template, context,
			context_instance=RequestContext(request))
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.options import get_verbose_name as convert_camelcase
from django.forms import Form, CheckboxSelectMultiple
from django.forms.models import modelform_factory, inlineformset_factory, _get_foreign_key
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict
from django.utils.text import capfirst
from stepping_out.modules.modules import ModuleModel, ModuleMultiModel, ModuleInlineModel


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
	
	def get_context(self, **kwargs):
		defaults = {
			'sections': self.admin_site.sections
		}
		defaults.update(kwargs)
		return defaults
	
	def has_permission(self, request):
		if request.user.is_active and request.user.is_authenticated():
			return True
		
		return False
	
	def view(self, request):
		weaver = Weaver(self, request)
		import pdb
		pdb.set_trace()
		if request.method == 'POST':
			invalid = []
			
			for sub in self.subs + self.inlines:
				sub.instantiate(request)
				if not sub.is_valid():
					invalid.append(sub)
			
			if not invalid:
				for sub in self.subs+self.inlines:
					sub.save()
				return HttpResponseRedirect('')
			
			form = self(request, request.POST, request.FILES)
		else:
			# need to set initial data from the db.
			initial = {}
			for sub in self.subs:
				sub.instantiate(request)
				initial.update(sub.initial)
			
			for sub in self.inlines:
				sub.instantiate(request)
			
			form = self(request, initial=initial)
		
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
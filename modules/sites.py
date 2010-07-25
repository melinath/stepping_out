from django.conf.urls.defaults import patterns, include, url
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy, ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from stepping_out.modules.admin import ModuleAdmin
from stepping_out.modules.modules import Module
from django import forms


ERROR_MESSAGE = ugettext_lazy("Please enter a correct username and password. Note that both fields are case-sensitive.")
LOGIN_FORM_KEY = 'this_is_the_login_form'


class OrderedDict(SortedDict):
	"""
	A sorted dictionary that defines a sort method for ordering. It accepts args
	for the sorting function on init.
	"""
	def __init__(self, data=None, *args, **kwargs):
		self.sorting_args = (args, kwargs,)
	
	def sort(self):
		if getattr(self, 'sorted', False):
			return
		
		args, kwargs = self.sorting_args
		self.keyOrder = [k for k,v in sorted(self.raw_items(), *args, **kwargs)]
		self.sorted = True
	
	def __setitem__(self, key, value):
		if key not in self:
			self.keyOrder.append(key)
			self.sorted = False
		super(SortedDict, self).__setitem__(key, value)
	
	def __iter__(self):
		self.sort()
		return super(OrderedDict, self).__iter__()
	
	def raw_items(self):
		"For fetching the dict items for sorting."
		return super(SortedDict, self).items()
	
	def items(self):
		self.sort()
		return super(OrderedDict, self).items()
	
	def iteritems(self):
		self.sort()
		return super(OrderedDict, self).iteritems()
	
	def keys(self):
		self.sort()
		return super(OrderedDict, self).keys()
	
	def iterkeys(self):
		self.sort()
		return super(OrderedDict, self).iterkeys()
	
	def values(self):
		self.sort()
		return super(OrderedDict, self).values()
	
	def itervalues(self):
		self.sort()
		return super(OrderedDict, self).itervalues()
	
	def setdefault(self, key, default):
		if key not in self:
			self.keyOrder.append(key)
			self.sorted = False
		return super(SortedDict, self).setdefault(key, default)
	
	def value_for_index(self, index):
		self.sort()
		return super(OrderedDict, self).value_for_index(self, index)
	
	def insert(self, index, key, value):
		self.sorted = False
		super(OrderedDict, self).insert(index, key, value)
	
	def copy(self):
		obj = super(OrderedDict, self).copy()
		obj.sorted = self.sorted
		return obj
	
	def clear(self):
		super(OrderedDict, self).clear()
		self.sorted = True


class LoginForm(forms.Form):
	this_is_the_login_form = forms.BooleanField(widget=forms.HiddenInput, initial=True)
	username = forms.CharField(max_length=30)
	password = forms.CharField(max_length=128, widget=forms.PasswordInput)


class AlreadyRegistered(Exception):
	pass


class NotRegistered(KeyError):
	pass


class ModuleAdminSite(object):
	url_prefix = 'stepping_out_admin'
	login_template = 'stepping_out/modules/login.html'
	logout_template = 'stepping_out/modules/logout.html'
	home_template = 'stepping_out/modules/home.html'
	
	def __init__(self):
		self._registry = OrderedDict(key=lambda t: t[1].order)
	
	def register(self, module, admin=ModuleAdmin):
		"""
		Registers a given module with a UserAdminSite instance.
		"""
		if not issubclass(module, Module):
			raise TypeError('%s must be a subclass of %s' %
				(module, Module.__name__))
		
		if module in self._registry:
			raise AlreadyRegistered('The module %s is already registered' %
				module)
		
		self._registry[module] = admin(self, module)
	
	def get_module(self, slug):
		for module in self._registry:
			if module.slug == slug:
				return module
		
		raise NotRegistered("Module with slug '%s' not found in registry")
	
	@property
	def modules(self):
		return self._registry
	
	def admin_view(self, view, cacheable=False, test=None):
		"""
		Decorator to apply common decorators to views for this admin.
		"""
		# FIXME: prohibit caching?
		def inner(request, *args, **kwargs):
			if not self.has_permission(request):
				return self.login(request)
			return view
		inner = csrf_protect(inner)
		return view
	
	def get_urls(self):
		def wrap(view, cacheable=False):
			return self.admin_view(view, cacheable) # (*args, **kwargs)
		
		urlpatterns = patterns('',
			url(r'^$', wrap(self.home), name='%s_root' % self.url_prefix),
			url(r'^logout/$', self.logout,
				name='%s_logout' % self.url_prefix),
		)
		
		for admin in self._registry.values():
			urlpatterns += patterns('',
				url(r'^%s/$' % admin.slug, include(admin.urls)),
			)
		
		return urlpatterns
	
	@property
	def urls(self):
		return self.get_urls()
	
	def get_context(self):
		return {'modules': self.modules}
	
	def home(self, request):
		try:
			return HttpResponseRedirect(self.get_module('home').absolute_url)
		except NotRegistered:
			return render_to_response(
				self.home_template,
				self.get_context(),
				context_instance=RequestContext(request)
			)
		except:
			raise
	
	def display_login_form(self, request, message):
		request.session.set_test_cookie()
		if request.POST:
			form = LoginForm(request.POST)
		else:
			form = LoginForm()
		context = {
			'message': message,
			'form': form
		}
		return render_to_response(
			self.login_template,
			context,
			context_instance = RequestContext(request)
		)
	
	def login(self, request):
		"""
		Displays the login form for the given HttpRequest.
		"""
		from django.contrib.auth.models import User
		
		# If this isn't already the login page, display it.
		if not request.POST.has_key(LOGIN_FORM_KEY):
			if request.POST:
				message = _("Please log in again, because your session has expired.")
			else:
				message = ""
			return self.display_login_form(request, message)

		# Check that the user accepts cookies.
		if not request.session.test_cookie_worked():
			message = _("Looks like your browser isn't configured to accept cookies. Please enable cookies, reload this page, and try again.")
			return self.display_login_form(request, message)
		else:
			request.session.delete_test_cookie()

		# Check the password.
		username = request.POST.get('username', None)
		password = request.POST.get('password', None)
		user = authenticate(username=username, password=password)
		if user is None:
			message = ERROR_MESSAGE
			if username is not None and u'@' in username:
				# Mistakenly entered e-mail address instead of username? Look it up.
				try:
					user = User.objects.get(email=username)
				except (User.DoesNotExist, User.MultipleObjectsReturned):
					message = _("Usernames cannot contain the '@' character.")
				else:
					if user.check_password(password):
						message = _("Your e-mail address is not your username."
									" Try '%s' instead.") % user.username
					else:
						message = _("Usernames cannot contain the '@' character.")
			return self.display_login_form(request, message)

		# The user data is correct; log in the user in and continue.
		else:
			if user.is_active and user.is_staff:
				login(request, user)
				return HttpResponseRedirect(request.get_full_path())
			else:
				return self.display_login_form(request, ERROR_MESSAGE)
	login = never_cache(login)
	
	def logout(self, request):
		from django.contrib.auth.views import logout
		defaults = {}
		if self.logout_template is not None:
			defaults['template_name'] = self.logout_template
		return logout(request, **defaults)

site = ModuleAdminSite()
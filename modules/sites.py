from django.conf.urls.defaults import patterns, include, url
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy, ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from stepping_out.modules.sections import Section
from django import forms


ERROR_MESSAGE = ugettext_lazy("Please enter a correct username and password. Note that both fields are case-sensitive.")
LOGIN_FORM_KEY = 'this_is_the_login_form'


class LoginForm(forms.Form):
	this_is_the_login_form = forms.BooleanField(widget=forms.HiddenInput, initial=True)
	username = forms.CharField(max_length=30)
	password = forms.CharField(max_length=128, widget=forms.PasswordInput)


class AlreadyRegistered(Exception):
	pass


class ModuleAdminSite(object):
	url_prefix = 'stepping_out_admin'
	login_template = 'stepping_out/modules/login.html'
	logout_template = 'stepping_out/modules/logout.html'
	
	def __init__(self):
		self._registry = {}
	
	def register(self, section):
		"""
		Registers a given section with a UserAdminSite instance.
		"""
		if not issubclass(section, Section):
			raise TypeError('%s must be a subclass of %s.Section' %
				(section, Section.__module__))
		
		if section in self._registry.values():
			raise AlreadyRegistered('The section %s is already registered' %
				section)
		
		self._registry[section.slug] = section(self)
	
	@property
	def sections(self):
		return self._registry.values()
	
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
		
		for section in self._registry.values():
			urlpatterns += patterns('',
				url(r'^%s/$' % section.slug, include(section.urls)),
			)
		
		return urlpatterns
	
	@property
	def urls(self):
		return self.get_urls()
	
	def home(self, request):
		if 'home' in self._registry:
			return HttpResponseRedirect(self._registry['home'].absolute_url)
		
		return render_to_response(
			self.home_template,
			context_instance=RequestContext(request)
		)
	
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
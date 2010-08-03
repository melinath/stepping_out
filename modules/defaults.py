from stepping_out.auth.forms import PrimaryUserEmailFormSet
from stepping_out.auth.models import UserEmail
from stepping_out.mail.models import MailingList
from stepping_out.modules.admin import ModuleAdmin
from stepping_out.modules.fields import ChoiceOfManyField, ProxyField, InlineField
from stepping_out.modules.models import ModelProxy
from stepping_out.modules.modules import Module
from stepping_out.modules.sites import site
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext


class UserProxy(ModelProxy):
	model = User


class UserEmailProxy(ModelProxy):
	model = UserEmail
	related_field_name = 'user'


class MailingListProxy(ModelProxy):
	model = MailingList
	related_field_name = 'subscribed_users'


class HomeModule(Module):
	slug = 'home'
	verbose_name = 'Home'


class HomeModuleAdmin(ModuleAdmin):
	order = 0
	template = 'stepping_out/modules/home.html'


class ChangePasswordModule(Module):
	slug = 'password'
	verbose_name = 'Change Password'


class ChangePasswordModuleAdmin(ModuleAdmin):
	order = 10
	template = 'stepping_out/modules/password_change_form.html'
	done_template = 'stepping_out/modules/password_change_done.html'
	
	@property
	def urls(self):
		from django.conf.urls.defaults import patterns, url
		
		def wrap(view, cacheable=False):
			return self.admin_site.admin_view(view, cacheable)
		
		urlpatterns = patterns('',
			url(r'^change/$', wrap(self.change_view),
				name='%s_password_change' % self.admin_site.url_prefix),
			url(r'^done/$', wrap(self.done_view),
				name='%s_password_change_done' % self.admin_site.url_prefix)
		)
		return urlpatterns
	
	def get_absolute_url(self):
		return reverse('%s_password_change' % (self.admin_site.url_prefix))
	absolute_url = property(get_absolute_url)
	
	def change_view(self, request, password_change_form=PasswordChangeForm):
		post_change_redirect = reverse('%s_password_change_done' % self.admin_site.url_prefix)
		
		if request.method == "POST":
			form = password_change_form(user=request.user, data=request.POST)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect(post_change_redirect)
		else:
			form = password_change_form(user=request.user)
		
		context = self.get_context()
		context.update({'form': form})
		
		return render_to_response(self.template, context,
				context_instance=RequestContext(request))
	
	def done_view(self, request):
		return render_to_response(self.done_template, self.get_context(),
			context_instance=RequestContext(request))


class UserSettingsModule(Module):
	verbose_name = "Account preferences"
	slug = "preferences"
	help_text = "Here you can set all sorts of exciting profile information!"
	first_name = ProxyField(UserProxy)
	last_name = ProxyField(UserProxy)
	emails = InlineField(UserEmailProxy, fields=['email'], extra=1,
		formset=PrimaryUserEmailFormSet, help_text="Email sent to a mailing list will be accepted as from you for any of your emails. You will receive email from mailing lists at your primary address.")


class UserSettingsAdmin(ModuleAdmin):
	order = 20


class MailingListModule(Module):
	verbose_name = "Mailing list subscriptions"
	slug = 'subscriptions'
	mailing_lists = ChoiceOfManyField(MailingListProxy, required=False)


class MailingListAdmin(ModuleAdmin):
	order = 30


site.register(UserSettingsModule, UserSettingsAdmin)
site.register(MailingListModule, MailingListAdmin)
site.register(HomeModule, HomeModuleAdmin)
site.register(ChangePasswordModule, ChangePasswordModuleAdmin)
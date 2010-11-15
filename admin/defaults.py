from stepping_out.mail.forms import ManageSubscriptionsForm
from stepping_out.mail.models import MailingList, UserEmail
from stepping_out.admin.admin import AdminSection, FormAdminSection, QuerySetAdminSection
from stepping_out.admin.sites import site
from stepping_out.admin.forms import UserSettingsForm, NewUserEmailFormSet, UserEmailForm
from stepping_out.auth.tokens import email_token_generator
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader, Context
from django.utils.http import int_to_base36


class HomeSection(AdminSection):
	slug = 'home'
	verbose_name = 'Home'
	order = 0
	template = 'stepping_out/admin/sections/home.html'


class ChangePasswordSection(AdminSection):
	order = 10
	template = 'stepping_out/admin/sections/password_change.html'
	slug = 'password'
	verbose_name = 'Change Password'
	
	def basic_view(self, request, password_change_form=PasswordChangeForm, extra_context=None):
		if request.method == "POST":
			form = password_change_form(user=request.user, data=request.POST)
			if form.is_valid():
				form.save()
				messages.add_message(request, messages.SUCCESS, "Password changed.")
				return HttpResponseRedirect('')
		else:
			form = password_change_form(user=request.user)
		
		context = self.get_context()
		context.update(extra_context or {})
		context.update({'form': form, 'navbar': self.admin_site.get_nav(request)})
		
		return render_to_response(self.template, context,
				context_instance=RequestContext(request))


class UserSettingsAdmin(FormAdminSection):
	verbose_name = "Account preferences"
	slug = "preferences"
	help_text = "Here you can set all sorts of exciting profile information!"
	template = 'stepping_out/admin/sections/account.html'
	order = 20
	form = UserSettingsForm
	formset = inlineformset_factory(User, UserEmail, UserEmailForm, NewUserEmailFormSet, can_delete=False)
	
	def basic_view(self, request, extra_context=None):
		if request.method == 'POST':
			form = self.form(request.POST, request.FILES, instance=request.user)
			formset = self.formset(request.POST, request.FILES, instance=request.user)
			
			if form.is_valid() and formset.is_valid():
				form.save()
				new = formset.save()
				if new:
					site = Site.objects.get_current()
					t = loader.get_template('stepping_out/admin/email/add_email_confirmation.txt')
					for email in new:
						url = reverse("%s_email_add" % self.admin_site.url_prefix, kwargs={
							'token': email_token_generator.make_token(request.user, email),
							'eidb36': int_to_base36(email.id),
							'uidb36': int_to_base36(request.user.id),
						})
						c = Context({
							'protocol': 'http',
							'domain': site.domain,
							'url': url,
							'admin_email': "the webmaster" # FIXME
						})
						send_mail("Confirm email for account", t.render(c),
							"noreply@%s" % site.domain, [email.email])
					if len(new) == 1:
						messages.add_message(request, messages.SUCCESS, "An email with a confirmation link has been sent to %s." % new[0].email)
					else:
						messages.add_message(request, messages.SUCCESS, "Confirmation links have been sent via email to the addresses you added.")
				return HttpResponseRedirect('')
		else:
			form = self.form(instance=request.user)
			formset = self.formset(instance=request.user)
		
		extra_context = extra_context or {}
		extra_context.update({
			'form': form,
			'formset': formset,
		})
		return super(FormAdminSection, self).basic_view(request, extra_context)


class SubscriptionAdmin(FormAdminSection):
	order = 30
	verbose_name = "Mailing list subscriptions"
	slug = 'subscriptions'
	form = ManageSubscriptionsForm
	template = 'stepping_out/admin/sections/subscriptions.html'
	
	def basic_view(self, request, extra_context=None):
		if request.method == 'POST':
			form = self.form(request.user, request.POST, request.FILES)
			
			if form.is_valid():
				form.save()
				return HttpResponseRedirect('')
		else:
			form = self.form(request.user)
		
		forced_lists = MailingList.objects.filter(
			Q(subscribed_groups__user=request.user) |
			Q(subscribed_officer_positions__users=request.user) |
			Q(moderator_users=request.user) |
			Q(moderator_groups__user=request.user) |
			Q(moderator_officer_positions__users=request.user) |
			Q(moderator_emails__user=request.user)
		)
		extra_context = extra_context or {}
		extra_context.update({
			'form': form,
			'forced_lists': forced_lists
		})
		return super(FormAdminSection, self).basic_view(request, extra_context)


#class MailingListConfigurationModule(QuerySetModule):
#	model = MailingList
#	slug = 'mailing-lists'
#	verbose_name = 'Manage Mailing Lists'
#
#
#class MailingListConfigurationAdmin(QuerySetModuleAdmin):
#	order = 40


site.register(HomeSection)
site.register(ChangePasswordSection)
site.register(UserSettingsAdmin)
site.register(SubscriptionAdmin)
#site.register(MailingListConfigurationModule, MailingListConfigurationAdmin)
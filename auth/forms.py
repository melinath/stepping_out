from django.forms.models import BaseInlineFormSet, BaseModelForm, ModelForm, DELETION_FIELD_NAME, construct_instance
from django.forms.widgets import RadioSelect
from stepping_out.auth.models import UserEmail, PendConfirmation
from stepping_out.auth.widgets import EmailInput
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm, PasswordChangeForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _


ADD_NEW = 'new'
DELETE = 'delete'
ACTION_CHOICES = (
	(ADD_NEW, 'New'),
	(DELETE, 'Delete')
)


def pend_action(form, obj, action):
	if action not in dict(ACTION_CHOICES).keys():
		raise ValueError #?
	
	if obj is None:
		obj = form.instance
	
	if action == DELETE:
		pend_obj = obj
	elif action == ADD_NEW:
		opts = form._meta
		pend_obj = construct_instance(form, obj, opts.fields, opts.exclude)
	
	pend = PendConfirmation(
		content_type = ContentType.objects.get_for_model(pend_obj),
		object_id = pend_obj.pk,
		action = action
	)
	pend.save()
	
	if action == ADD_NEW:
		opts = pend_obj._meta
		for f in opts.fields:
			#if isinstance(f, models.AutoField):
			#	continue
			if f.value_from_object(pend_obj):
				pend.kv_pairs.create(key=f.attname, value=f.value_from_object(pend_obj))
	
	return pend


class PendConfirmationFormSet(BaseInlineFormSet):
	"""Forms in this formset are saved as "requiring email confirmation".
	"""
	email_template_name = 'stepping_out/registration/pended_action_email.html'
	
	def __init__(self, *args, **kwargs):
		self._messages = []
		super(PendConfirmationFormSet, self).__init__(*args, **kwargs)
	
	def save_existing_objects(self, commit=True):
		self._pend_delete = []
		if not self.get_queryset():
			return []
		
		to_save = []
		for form in self.initial_forms:
			pk_name = self._pk_field.name
			raw_pk_value = form._raw_value(pk_name)
			
			pk_value = form.fields[pk_name].clean(raw_pk_value)
			pk_value = getattr(pk_value, 'pk', pk_value)
			
			obj = self._existing_object(pk_value)
			if self.can_delete:
				raw_delete_value = form._raw_value(DELETION_FIELD_NAME)
				should_delete = form.fields[DELETION_FIELD_NAME].clean(raw_delete_value)
				if should_delete:
					self.pend_delete(form, obj)
					continue
			# people shouldn't be allowed to change existing items. just confuses things.
			continue
		return self._pend_delete
	
	def save_new_objects(self, commit=True):
		self._pend_new = []
		for form in self.extra_forms:
			if not form.has_changed():
				continue
			if self.can_delete:
				raw_delete_value = form._raw_value(DELETION_FIELD_NAME)
				should_delete = form.fields[DELETION_FIELD_NAME].clean(raw_delete_value)
				if should_delete:
					continue
			self.pend_new(form)
		return self._pend_new
	
	def pend_email(self, pend, email, subject="Confirmation email", context=None):
		if email is None:
			return
		current_site = Site.objects.get_current()
		from_email = getattr(settings, 'STEPPING_OUT_NOREPLY_EMAIL', 'noreply@%s' % current_site.domain)
		t = loader.get_template(self.email_template_name)
		c = {
			'message': 'The following action has been pended: %s.',
			'domain': current_site.domain,
			'site_name': current_site.name,
			'code': pend.code,
			'admin_email': 'admin_email', # FIXME
			'protocol': 'http',
		}
		if context is not None:
			c.update(context)
		
		send_mail(subject, t.render(Context(c)), from_email, [email])
	
	def pend_delete(self, form, obj, email=None, subject="Confirmation email", context=None):
		pend = pend_action(form, obj, DELETE)
		
		self.pend_email(pend, email, subject, context)
		
		self._pend_delete.append(pend)
		self._messages.append((messages.SUCCESS, "Pended %s" % pend))
	
	def pend_new(self, form, email=None, subject="Confirmation email", context=None):
		pend = pend_action(form, None, ADD_NEW)
		
		self.pend_email(pend, email, subject, context)
		
		self._pend_new.append(pend)
		self._messages.append((messages.SUCCESS, "Pended %s" % pend))
	
	@property
	def messages(self):
		# should I make this a copy?
		messages = self._messages
		for form in self.forms:
			try:
				messages.extend(form.messages)
			except:
				pass
		return messages


class PrimaryUserEmailFormSet(PendConfirmationFormSet):
	radio_name = 'primary_email'
	radio = RadioSelect()
	
	@property
	def radio_value(self):
		try:
			return self.queryset.get(email=self.instance.email).pk
		except UserEmail.DoesNotExist:
			return None
	
	@property
	def radio_choices(self):
		if not hasattr(self, '_choices'):
			self._choices = [(m.pk, m.email) for m in self.queryset]
		return self._choices
	
	@property
	def radio_renderer(self):
		return self.radio.get_renderer(self.radio_name, self.radio_value,
			choices=self.radio_choices)
	
	@property
	def radio_value_from_datadict(self):
		return self.radio.value_from_datadict(self.data, self.files,
			self.radio_name) or self.radio_choices[0][0]
	
	def add_fields(self, form, index):
		super(PrimaryUserEmailFormSet, self).add_fields(form, index)
		try:
			#FIXME: Better way to do this?
			form.primary_widget = self.radio_renderer[index]
		except IndexError:
			pass
		
		form.fields['email'].widget = EmailInput(form.fields['email'].widget.attrs)
		if index is not None and index < self.initial_form_count():
			form.fields['email'].widget.attrs['readonly'] = 'readonly'
	
	def save(self, commit=True):
		saved = super(PrimaryUserEmailFormSet, self).save(commit)
		
		value = self.radio_value_from_datadict
		email = self.queryset.get(pk=value)
		self.instance.email = email.email
		self.instance.save()
		
		return saved
	
	def pend_delete(self, form, obj):
		pend = pend_action(form, obj, DELETE)
		
		current_site = Site.objects.get_current()
		email = pend.item.email
		context = {
			'message': "This email has been attached to an account at %s and you've asked to remove it." % current_site.name
		}
		self.pend_email(pend, email, context=context)
		
		# FIXME: better message
		self._pend_delete.append(pend)
		self._messages.append((messages.SUCCESS, "A confirmation email has been sent to %s. Click the link in the email to remove %s from your emails." % (email, email)))
	
	def pend_new(self, form):
		# FIXME: can I combine this w/ pend_delete?
		pend = pend_action(form, None, ADD_NEW)
		
		current_site = Site.objects.get_current()
		email = pend.kv_pairs.get(key='email').value
		context = {
			'message': "You've asked to add this email to your account at %s." % current_site.name
		}
		self.pend_email(pend, email, context=context)
		
		self._pend_new.append(pend)
		self._messages.append((messages.SUCCESS, "A confirmation email has been sent to %s. Click the link in the email to add %s to your emails." % (email, email)))


class UserEmailPasswordResetForm(PasswordResetForm):
	def clean_email(self):
		"""
		Validates that a user exists with the given e-mail address.
		"""
		email = self.cleaned_data['email']
		self.users_cache = User.objects.filter(emails__email__iexact=email)
		if len(self.users_cache) == 0:
			raise forms.ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
		return email
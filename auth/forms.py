from django.forms.models import BaseInlineFormSet, BaseModelForm, ModelForm, DELETION_FIELD_NAME, construct_instance
from django.forms.widgets import RadioSelect
from stepping_out.auth.models import UserEmail, PendConfirmation, PendConfirmationData
from stepping_out.auth.widgets import EmailInput
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django import forms
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _
from random import choice


ADD_NEW = 'new'
DELETE = 'delete'
ACTION_CHOICES = (
	(ADD_NEW, 'New'),
	(DELETE, 'Delete')
)


class RequiredFormSet(forms.formsets.BaseFormSet):
	def _get_deleted_forms(self):
		deleted_forms = super(RequiredFormSet, self)._get_deleted_forms()
		if len(deleted_forms) == len(self.forms):
			raise Exception("You need to have at least one.")
		return deleted_forms


class RequiredInlineFormSet(RequiredFormSet, forms.models.BaseInlineFormSet):
	pass


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
	
	if action == DELETE:
		pend.save()
	elif action == ADD_NEW:
		# then make sure that a pended object with the same kv_pairs doesn't already exist
		opts = pend_obj._meta
		
		f = opts.fields[0]
		potentials = [kv_pair.confirmation for kv_pair in PendConfirmationData.objects.filter(key=f.attname, value=f.value_from_object(pend_obj)) if kv_pair.confirmation.content_type == pend.content_type]
		
		for potential in potentials:
			for f in opts.fields:
				if f.value_from_object(pend_obj):
					try:
						potential.kv_pairs.get(key=f.attname, value=f.value_from_object(pend_obj))
					except PendConfirmationData.DoesNotExist:
						break
			else:
				# There is one!
				return potential
		
		pend.save()
		for f in opts.fields:
			if f.value_from_object(pend_obj):
				pend.kv_pairs.create(key=f.attname, value=f.value_from_object(pend_obj))
	
	return pend
	
def pend_email(pend, email, subject="Confirmation email", context=None,
			   email_template_name='stepping_out/registration/pended_action_email.html'):
	if email is None:
		return
	current_site = Site.objects.get_current()
	from_email = getattr(settings, 'STEPPING_OUT_NOREPLY_EMAIL', 'noreply@%s' % current_site.domain)
	t = loader.get_template(email_template_name)
	c = {
		'message': 'The following action has been pended: %s.' % pend,
		'domain': current_site.domain,
		'site_name': current_site.name,
		'code': pend.code,
		'admin_email': 'admin_email', # FIXME
		'protocol': 'http',
	}
	if context is not None:
		c.update(context)
	
	send_mail(subject, t.render(Context(c)), from_email, [email])


class PendConfirmationFormSet(RequiredInlineFormSet):
	"""Forms in this formset are saved as "requiring email confirmation".
	"""
	def __init__(self, *args, **kwargs):
		self._messages = []
		super(PendConfirmationFormSet, self).__init__(*args, **kwargs)
	
	@property
	def pending_deletion(self):
		# can I do this generically?
		raise NotImplementedError
	
	@property
	def pending_addition(self):
		# can I do this generically?
		raise NotImplementedError
	
	def save_existing_objects(self, commit=True):
		self._pend_delete = []
		if not self.get_queryset():
			return []
		
		to_delete = []
		pending_deletion = self.pending_deletion
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
					for confirmation in pending_deletion:
						if confirmation.item == obj:
							break
					else:
						to_delete.append((form, obj))
					continue
				else:
					for confirmation in pending_deletion:
						if confirmation.item == obj:
							#pending_deletion.remove(confirmation)
							confirmation.delete()
			# people shouldn't be allowed to change existing items. just confuses things.
			continue
		
		if self.required and len(to_delete) + len(pending_deletion) >= self.initial_form_count():
			self._messages.append((messages.ERROR, "You can't delete all the items!"))
		else:
			for form, obj in to_delete:
				self.pend_delete(form, obj)
		
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
	
	def pend_delete(self, form, obj, email=None, subject="Confirmation email", context=None):
		pend = pend_action(form, obj, DELETE)
		
		pend_email(pend, email, subject, context)
		
		self._pend_delete.append(pend)
		self._messages.append((messages.SUCCESS, "Pended %s" % pend))
	
	def pend_new(self, form, email=None, subject="Confirmation email", context=None):
		pend = pend_action(form, None, ADD_NEW)
		
		pend_email(pend, email, subject, context)
		
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
	
	def add_fields(self, form, index):
		super(PendConfirmationFormSet, self).add_fields(form, index)
		if form.instance in self.pending_deletion_items:
			form.fields[DELETION_FIELD_NAME].initial = True


class PrimaryUserEmailFormSet(PendConfirmationFormSet):
	radio_name = 'primary_email'
	radio = RadioSelect()
	
	@property
	def pending_deletion(self):
		ids = [item.pk for item in self.queryset]
		return set([confirmation for confirmation in PendConfirmation.objects.filter(
				content_type=ContentType.objects.get_for_model(UserEmail),
				object_id__in=ids
		)])
	
	@property
	def pending_deletion_items(self):
		return [confirmation.item for confirmation in self.pending_deletion]
	
	@property
	def pending_addition(self):
		return set([
			data.confirmation for data in PendConfirmationData.objects.filter(
				confirmation__content_type=ContentType.objects.get_for_model(UserEmail),
				confirmation__object_id=None,
				key='user_id', value=self.instance.pk
			)
		])
	
	@property
	def pending(self):
		return self.pending_deletion | self.pending_addition
	
	@property
	def radio_value(self):
		try:
			return self.queryset.get(email=self.instance.email).pk
		except UserEmail.DoesNotExist:
			return None
	
	@property
	def radio_choices(self):
		return [(m.pk, m.email) for m in self.queryset]
	
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
		widgets = dict([(int(radio_input.choice_value), radio_input) for radio_input in self.radio_renderer])
		
		try:
			form.primary_widget = widgets[form.instance.pk]
		except KeyError:
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
		pend_email(pend, email, context=context)
		
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
		pend_email(pend, email, context=context)
		
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


class PendUserCreationForm(UserCreationForm):
	email = forms.EmailField(widget=EmailInput)
	
	def __init__(self, *args, **kwargs):
		super(PendUserCreationForm, self).__init__(*args, **kwargs)
		self._messages = []
	
	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			UserEmail.objects.get(email=email)
		except UserEmail.DoesNotExist:
			return email
		raise forms.ValidationError(_("A user already exists with that email."))
	
	def save(self, commit=True):
		user = super(PendUserCreationForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		pend = pend_action(self, user, ADD_NEW)
		current_site = Site.objects.get_current()
		email_context = {
			'message': "You've requested an account at %s." % current_site.domain
		}
		pend_email(pend, user.email, "Account creation confirmation", email_context)
		return pend
	
	@property
	def messages(self):
		return self._messages


class TestHumanityForm(forms.Form):
	HUMANITY_CHECKS = {
		'first-letter': ('What is the first letter of the English alphabet?', 'a'),
		'5-times-5': ('What is 5 times 5?', '25'),
		'fitzgerald': ('How many letters are in the name Fitzgerald?', '10'),
		'last-name': ("What was Duke Ellington's last name?", 'Ellington'),
		'sentence': ("This is a really silly question, but what is the fourth word in this sentence?", 'really'),
	}
	question = forms.CharField(max_length=20, widget=forms.HiddenInput)
	answer = forms.CharField(max_length=20, help_text="This is a (case-sensitive) question to make sure you're human. :-)")
	
	def __init__(self, *args, **kwargs):
		super(TestHumanityForm, self).__init__(*args, **kwargs)
		initial = choice(self.HUMANITY_CHECKS.keys())
		self.fields['question'].initial = initial
	
	def get_question(self):
		key = self['question'].data or self.fields['question'].initial
		return self.HUMANITY_CHECKS[key][0]
	
	def clean_question(self):
		question = self.cleaned_data['question']
		if question not in self.HUMANITY_CHECKS:
			raise ValidationError("Invalid question. This should only happen if you've been messing with the HTML. Please don't. Thanks!")
		return question
	
	def clean_answer(self):
		correct_answer = self.HUMANITY_CHECKS[self.cleaned_data['question']][1]
		answer = self.cleaned_data['answer']
		if answer != correct_answer:
			raise ValidationError("Wrong! Try again.")
		return answer
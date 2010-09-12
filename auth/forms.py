from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django import forms
from django.forms.models import BaseInlineFormSet, BaseModelForm, ModelForm, DELETION_FIELD_NAME, construct_instance
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _
from stepping_out.auth.tokens import REGISTRATION_TIMEOUT_DAYS
from stepping_out.auth.widgets import EmailInput
from stepping_out.mail.models import UserEmail
from random import choice
import datetime


class RequiredFormSet(forms.formsets.BaseFormSet):
	def _get_deleted_forms(self):
		deleted_forms = super(RequiredFormSet, self)._get_deleted_forms()
		if len(deleted_forms) == len(self.forms):
			raise Exception("You need to have at least one.")
		return deleted_forms


class RequiredInlineFormSet(RequiredFormSet, forms.models.BaseInlineFormSet):
	pass


class UserEmailForm(forms.ModelForm):
	def validate_unique(self):
		# This should just do nothing. This form doesn't ever create anything,
		# so we don't need to make sure the instance is unique.
		pass
	
	def save(self, commit=True):
		import pdb
		pdb.set_trace()
		try:
			# Never create a double email.
			instance = UserEmail.objects.get(email=self.instance.email)
		except UserEmail.DoesNotExist:
			instance = super(UserEmailForm, self).save(commit=False)
			
			# New instances shouldn't be tied to a user until confirmation.
			instance.user = None
			instance.save()
		return instance
	
	class Meta:
		model = UserEmail


class PrimaryUserEmailFormSet(RequiredInlineFormSet):
	radio_name = 'primary_email'
	radio = RadioSelect()
	
	def __init__(self, *args, **kwargs):
		self._messages = []
		super(PrimaryUserEmailFormSet, self).__init__(*args, **kwargs)
	
	def save_existing_objects(self, commit=True):
		self.changed_objects = []
		self.deleted_objects = []
		if not self.get_queryset():
			return []
		
		to_delete = []
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
					to_delete.append(obj)
			# people shouldn't be allowed to change existing items. just confuses things.
			# Otherwise, changed objects would be saved here.
		
		if self.required and len(to_delete) >= self.initial_form_count():
			self._messages.append((messages.ERROR, "You can't delete all the items!"))
		else:
			for obj in to_delete:
				obj.delete()
			self.deleted_objects = to_delete
		
		return []
	
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
		# get saved objects, deleted objects. Perhaps do w/ override on save_existing/save_new.
		saved = super(PrimaryUserEmailFormSet, self).save(commit)
		
		value = self.radio_value_from_datadict
		email = self.queryset.get(pk=value)
		self.instance.email = email.email
		self.instance.save()
		
		return saved
	
	@property
	def messages(self):		# should I make this a copy?
		messages = self._messages
		for form in self.forms:
			try:
				messages.extend(form.messages)
			except:
				pass
		return messages


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
			User.objects.get(emails__email=email)
		except User.DoesNotExist:
			return email
		raise forms.ValidationError(_("A user already exists with that email."))
	
	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			return username
		
		# Consider the name free if more than the relevant number of days has passed.
		if not user.is_active and user.date_joined == user.last_login and (datetime.datetime.now() - user.date_joined).days > REGISTRATION_TIMEOUT_DAYS:
			user.delete()
			return username
		
		raise forms.ValidationError(_("A user with that username already exists."))
	
	def save(self, commit=True):
		user = super(PendUserCreationForm, self).save(commit=False)
		user.is_active = False
		user.email = self.cleaned_data['email']
		user.save()
		return user


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
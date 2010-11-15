from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from stepping_out.auth.widgets import EmailInput
from stepping_out.mail.models import UserEmail
import re


checkbox_re = re.compile('(<input[^>]+type="checkbox"[^>]+>)')
radio_re = re.compile('(<input[^>]+type="radio"[^>]+>)')


class UserSettingsForm(forms.ModelForm):
	email = forms.models.ModelChoiceField(UserEmail.objects.none(), widget=RadioSelect, empty_label=None)
	delete_emails = forms.models.ModelMultipleChoiceField(UserEmail.objects.none(), widget=forms.CheckboxSelectMultiple, required=False)
	
	def __init__(self, *args, **kwargs):
		super(UserSettingsForm, self).__init__(*args, **kwargs)
		user = self.instance
		self.fields['delete_emails'].queryset = user.emails.all()
		self.fields['email'].queryset = user.emails.all()
		try:
			self.initial['email'] = user.emails.get(email=user.email)
		except UserEmail.DoesNotExist:
			pass
	
	def clean_delete_emails(self):
		emails = self.cleaned_data['delete_emails']
		# is this the correct way to compare them?
		if isinstance(emails, list):
			count = len(emails) # Temporary HACK until ticket 14567 is resolved.
		else:
			count = emails.count()
		if count == self.instance.emails.count():
			raise ValidationError("At least one email is required.")
		return emails
	
	def clean_email(self):
		email = self.cleaned_data['email']
		return email.email
	
	def get_email_table_rows(self):
		delete_checkboxes = checkbox_re.finditer(self['delete_emails'].as_widget())
		primary_radios = radio_re.finditer(self['email'].as_widget())
		for email in self.instance.emails.all():
			yield email.email, primary_radios.next().group(0), delete_checkboxes.next().group(0)
	
	def save(self, commit=True):
		super(UserSettingsForm, self).save(commit)
		for email in self.cleaned_data['delete_emails']:
			email.delete()
	
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']


# Here's how it SHOULD work: PrimaryUserEmailFormSet has a clean method that
# checks that at least one existing form has data in it, since the new emails will
# be pended. Then on save, if an email is not already attached to the user, send
# a confirmation email to the email with a reversed token address.


class UserEmailForm(forms.ModelForm):
	def validate_unique(self):
		# This should just do nothing. This form doesn't ever create anything,
		# so we don't need to make sure the instance is unique.
		pass
	
	def save(self, commit=True):
		"""
		Return either a UserEmail object that already exists with the submitted
		email or a new UserEmail object that is associated with no user.
		"""
		try:
			instance = UserEmail.objects.get(email=self.instance.email)
		except UserEmail.DoesNotExist:
			instance = super(UserEmailForm, self).save(commit=False)
			instance.user = None
			instance.save()
		return instance
	
	class Meta:
		model = UserEmail


class NewUserEmailFormSet(BaseInlineFormSet):
	"""This form allows only the creation, not the deletion, of UserEmail
	instances for a given user."""
	def __init__(self, *args, **kwargs):
		kwargs['queryset'] = UserEmail.objects.none()
		super(NewUserEmailFormSet, self).__init__(*args, **kwargs)
	
	def save_existing_objects(self, commit=True):
		# There should never be changed or deleted objects here.
		self.changed_objects = []
		self.deleted_objects = []
		return []
	
	def save_new(self, form, commit=True):
		"""Send an email with an activation link to this email for completion
		of the process."""
		return form.save()
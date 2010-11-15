from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import ugettext_lazy as _
from stepping_out.auth.tokens import REGISTRATION_TIMEOUT_DAYS
from stepping_out.auth.widgets import EmailInput
from stepping_out.mail.models import UserEmail
from random import choice
import datetime


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
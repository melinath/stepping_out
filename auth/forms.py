from django.forms.models import BaseInlineFormSet, BaseModelForm, ModelForm
from django.forms.widgets import RadioSelect
from stepping_out.auth.models import UserEmail


class PrimaryUserEmailFormSet(BaseInlineFormSet):
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
			form.primary_widget = self.radio_renderer[index]
		except IndexError:
			pass
	
	def save(self, commit=True):
		saved = super(PrimaryUserEmailFormSet, self).save(commit)
		
		value = self.radio_value_from_datadict
		email = self.queryset.get(pk=value)
		self.instance.email = email.email
		self.instance.save()
		
		return saved
		


class PendConfirmationForm(BaseModelForm):
	"""Saves an intermediate confirmation model."""
	pass
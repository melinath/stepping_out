from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SlugListField(models.TextField):
	__metaclass__ = models.SubfieldBase
	description = _("Comma-separated slug field")
	
	def __init__(self, *args, **kwargs):
		if 'choices' in kwargs and hasattr(kwargs['choices'], '__call__'):
			self._choice_func = kwargs.pop('choices')
			kwargs['choices'] = self._choice_func()
		super(SlugListField, self).__init__(*args, **kwargs)
	
	def get_choices(self, **kwargs):
		# TODO: is there a more elegant way to force late evaluation?
		if hasattr(self, '_choice_func'):
			return self._choice_func()
		kwargs['include_blank'] = False
		return super(SlugListField, self).get_choices(**kwargs)
	
	def to_python(self, value):
		if not value:
			return []
		
		if isinstance(value, list):
			return value
		
		return value.split(',')
	
	def get_prep_value(self, value):
		return ','.join(value)
	
	def formfield(self, **kwargs):
		defaults = {'widget': forms.CheckboxSelectMultiple, 'choices': self.get_choices()}
		defaults.update(kwargs)
		# This is necessary because django hard-codes TypedChoiceField.
		form_class = forms.MultipleChoiceField
		return form_class(**defaults)
	
	def validate(self, value, model_instance):
		invalid_values = []
		for val in value:
			try:
				super(SlugListField, self).validate(val, model_instance)
			except ValidationError:
				invalid_values.append(val)
		
		if invalid_values:
			# should really make a custom message.
			raise ValidationError(self.error_messages['invalid_choice'] % invalid_values)
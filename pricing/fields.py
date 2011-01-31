from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SlugMultipleChoiceField(models.Field):
	__metaclass__ = models.SubfieldBase
	description = _("Comma-separated slug field")
	
	def get_internal_type(self):
		return "TextField"
	
	def to_python(self, value):
		if not value:
			return []
		
		if isinstance(value, list):
			return value
		
		return value.split(',')
	
	def get_prep_value(self, value):
		return ','.join(value)
	
	def formfield(self, **kwargs):
		# This is necessary because django hard-codes TypedChoiceField for things with choices.
		defaults = {
			'widget': forms.CheckboxSelectMultiple,
			'choices': self.get_choices(include_blank=False),
			'label': capfirst(self.verbose_name),
			'required': not self.blank,
			'help_text': self.help_text
		}
		if self.has_default():
			if callable(self.default):
				defaults['initial'] = self.default
				defaults['show_hidden_initial'] = True
			else:
				defaults['initial'] = self.get_default()
		
		for k in kwargs.keys():
			if k not in ('coerce', 'empty_value', 'choices', 'required',
						 'widget', 'label', 'initial', 'help_text',
						 'error_messages', 'show_hidden_initial'):
				del kwargs[k]
		
		defaults.update(kwargs)
		form_class = forms.TypedMultipleChoiceField
		return form_class(**defaults)
	
	def validate(self, value, model_instance):
		invalid_values = []
		for val in value:
			try:
				validate_slug(val)
			except ValidationError:
				invalid_values.append(val)
		
		if invalid_values:
			# should really make a custom message.
			raise ValidationError(self.error_messages['invalid_choice'] % invalid_values)


try:
	from south.modelsinspector import add_introspection_rules
except ImportError:
	pass
else:
	add_introspection_rules([], ["^stepping_out\.pricing\.fields\.SlugMultipleChoiceField"])
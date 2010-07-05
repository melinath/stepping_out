from django.forms.widgets import Input, Select, TextInput
from django.contrib.admin.widgets import AdminTextInputWidget
from django.utils.safestring import mark_safe


class EmailInput(Input):
	input_type = 'email'


class AdminEmailInputWidget(AdminTextInputWidget):
	input_type = 'email'


class SelectOther(Select):
	"""
	This widget offers a choice field and a text field. The text field value, if
	there is one, overrides the choice field value.
	"""
	def __init__(self, other=TextInput, attrs=None, choices=()):
		super(SelectOther, self).__init__(attrs, choices)
		self.other = other(attrs) # do I want to pass the attrs?
	
	def render(self, name, value, attrs=None, choices=()):
		option_keys = [choice[0] for choice in self.choices]
		if value in option_keys:
			othervalue = None
		else:
			othervalue = value
			value = None
		
		select = super(SelectOther, self).render(name, value, attrs, choices)
		text = self.other.render(name + '_text', othervalue, attrs)
		return mark_safe(u'\n'.join((select, text)))
	
	def value_from_datadict(self, data, files, name):
		othervalue = self.other.value_from_datadict(data, files, name + '_text')
		value = super(SelectOther, self).value_from_datadict(data, files, name)
		return othervalue or value
from django import forms


class DelayedDateForm(forms.ModelForm):
	date_field = 'date'
	
	def __init__(self, *args, **kwargs):
		super(DelayedDateForm, self).__init__(*args, **kwargs)
		self.fields[self.date_field].required = False


from django import forms
from stepping_out.events.models import Event


class EditEventForm(forms.ModelForm):
	def __init__(self, owner, *args, **kwargs):
		super(EditEventForm, self).__init__(*args, **kwargs)
		if self.instance.pk is None:
			self.instance.owner = owner
	
	class Meta:
		model = Event
		exclude = ('uid', 'owner', 'attendees')
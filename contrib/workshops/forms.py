from django.contrib import messages
from django.forms import ModelForm
from stepping_out.contrib.workshops.models import Workshop
from stepping_out.pricing.forms import PricePackageFormSet


class CreateWorkshopForm(ModelForm):
	def save(self, *args, **kwargs):
		instance = Workshop.objects.create_basic(name=self.cleaned_data['name'], tagline=self.cleaned_data['tagline'])
		instance.is_active = True
		return instance
	
	class Meta:
		model = Workshop
		fields = ['name', 'tagline']


class EditWorkshopForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(EditWorkshopForm, self).__init__(*args, **kwargs)
		self.subformset_instance = PricePackageFormSet(instance=self.instance)
		
	class Meta:
		model = Workshop
		exclude = ['registered_users', 'is_active']
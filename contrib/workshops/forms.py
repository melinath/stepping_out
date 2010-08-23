from django import forms
from django.contrib import messages
from django.forms import ModelForm, Form
from stepping_out.contrib.workshops.models import Workshop, WorkshopUserMetaInfo
from stepping_out.contrib.workshops.exceptions import RegistrationClosed
from stepping_out.pricing.forms import PricePackageFormSet
from stepping_out.pricing.models import PricePackage
import datetime


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


class WorkshopRegistrationForm(Form):
	dancing_as = WorkshopUserMetaInfo._meta.get_field('dancing_as').formfield()
	person_type = forms.CharField(max_length=15)
	
	def __init__(self, user, workshop, *args, **kwargs):
		self.user = user
		self.workshop = workshop
		# TODO: Insert something here to test if workshop registration is open.
		try:
			self.metainfo = WorkshopUserMetaInfo.objects.get(user=user, workshop=workshop)
		except WorkshopUserMetaInfo.DoesNotExist:
			self.metainfo = WorkshopUserMetaInfo(user=user, workshop=workshop)
		
		try:
			self.price_package = workshop.price_packages.filter(available_until__gte=datetime.date.today())[0]
		except IndexError:
			# If there aren't any price packages available, they can't register.
			# Treat as closed registration.
			raise RegistrationClosed
		
		super(WorkshopRegistrationForm, self).__init__(*args, **kwargs)
		
		#import pdb
		self.fields['person_type'].choices = [choice for choice in self.price_package._meta.get_field('person_types').choices if choice[0] in self.price_package.person_types]
		self.fields['price_option'] = forms.models.ModelChoiceField(queryset=self.price_package.options.all())
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from stepping_out.contrib.workshops.models import Workshop, Registration, WorkshopTrack
from stepping_out.housing import HOUSING_CHOICES
from stepping_out.housing.forms import OfferedHousingForm, RequestedHousingForm
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


WorkshopTrackInlineFormSet = forms.models.inlineformset_factory(Workshop, WorkshopTrack, extra=1)


class EditWorkshopForm(ModelForm):
	inlines = [WorkshopTrackInlineFormSet, PricePackageFormSet]
	
	def __init__(self, *args, **kwargs):
		super(EditWorkshopForm, self).__init__(*args, **kwargs)
		
		kwargs['instance'] = self.instance
		self.inline_instances = []
		for formset in self.inlines:
			self.inline_instances.append(formset(*args, **kwargs))
	
	def get_inline_instances(self):
		for formset_instance in self.inline_instances:
			opts = formset_instance.model._meta
			yield (opts.verbose_name_plural, opts.verbose_name, formset_instance.model.__name__, formset_instance,)
	
	def is_valid(self):
		if not super(EditWorkshopForm, self).is_valid():
			return False
		
		for formset in self.inline_instances:
			if not formset.is_valid():
				return False
		
		return True
	
	def save(self):
		super(EditWorkshopForm, self).save()
		for formset in self.inline_instances:
			formset.save()
	
	class Meta:
		model = Workshop
		exclude = ['registered_users']


def is_checked(value):
	"""A simple validator to make sure a field is checked."""
	try:
		if bool(value) is True:
			return True
	except:
		raise ValidationError("Invalid value")
	raise ValidationError("This box must be checked.")


class WorkshopRegistrationForm(ModelForm):
	person_type = forms.CharField(max_length=15, widget=forms.RadioSelect())
	housing = forms.CharField(max_length=1, widget=forms.RadioSelect(choices=HOUSING_CHOICES))
	waiver = forms.BooleanField(validators=[is_checked])
	
	def __init__(self, workshop, user=None, key=None, *args, **kwargs):
		self.user = user
		self.key = key
		self.workshop = workshop
		if user is None and key is None:
			instance = Registration(workshop=workshop)
		else:
			registration_kwargs = {'workshop': workshop}
			if user:
				registration_kwargs.update({'user': user})
			else:
				registration_kwargs.update({'key': key})
			
			#propogate a DoesNotExist.
			instance = Registration.objects.get(**registration_kwargs)
			
			initial = {
				'price_option': instance.price.option.pk,
				'person_type': instance.price.person_type,
				# If they're registered, presumably they agreed to the waiver.
				'waiver': True,
				'housing': workshop.housing.get_housing_status(user)
			}
			initial.update(kwargs.get('initial', {}))
			kwargs['initial'] = initial
		
		tracks = workshop.tracks.all()
		if len(tracks) == 1:
			initial = kwargs.get('initial', {})
			initial['track'] = tracks[0].id
			kwargs['initial'] = initial
		
		kwargs['instance'] = instance
		
		super(WorkshopRegistrationForm, self).__init__(*args, **kwargs)
		
		# Don't check whether there are any available: this form should only
		# be instantiated if registration is possible.
		price_package = workshop.price_packages.filter(available_until__gte=datetime.date.today())[0]
		
		self.fields['dancing_as'].widget = forms.RadioSelect(choices=self._meta.model._meta.get_field('dancing_as').get_choices(include_blank=False))
		self.fields['person_type'].widget.choices = [choice for choice in price_package._meta.get_field('person_types').choices if choice[0] in price_package.person_types]
		self.fields['price_option'] = forms.models.ModelChoiceField(empty_label=None, queryset=price_package.options.all(), widget=forms.RadioSelect())
		self.fields['track'] = forms.models.ModelChoiceField(workshop.tracks.all(), widget=forms.RadioSelect, empty_label=None)
		
		if user is None:
			self.fields['first_name'] = instance._meta.get_field('first_name').formfield(required=True)
			self.fields['last_name'] = instance._meta.get_field('last_name').formfield(required=True)
		else:
			self.fields['first_name'] = user._meta.get_field('first_name').formfield()
			self.fields['last_name'] = user._meta.get_field('last_name').formfield()
	
	def save(self, commit=True):
		self.instance.price = self.cleaned_data['price_option'].prices.get(person_type=self.cleaned_data['person_type'])
		instance = super(WorkshopRegistrationForm, self).save(commit=False)
		
		if 'first_name' in self.cleaned_data and 'last_name' in self.cleaned_data:
			if instance.user is None:
				instance.first_name, instance.last_name = self.cleaned_data['first_name'], self.cleaned_data['last_name']
			else:
				user = self.instance.user
				user.first_name, user.last_name = self.cleaned_data['first_name'], self.cleaned_data['last_name']
				user.save()
		if self.user is None and self.key is None:
			instance.key = instance.make_key()
		if commit:
			instance.save()
		return instance
	
	class Meta:
		model = Registration
		fields = ['track', 'dancing_as']
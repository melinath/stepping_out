from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from stepping_out.contrib.workshops.models import Workshop, Registration, WorkshopTrack, HousingOffer, HousingRequest
from stepping_out.pricing.forms import PricePackageFormSet
from stepping_out.pricing.models import PricePackage
import datetime


# Housing status things.
NEUTRAL = '0'
REQUESTED = '1'
OFFERED = '2'
HOUSING_CHOICES = (
	(NEUTRAL, "I do not need housing and I can't offer housing"),
	(REQUESTED, "I need housing"),
	(OFFERED, "I can offer housing"),
)


class HousingPhoneNumberForm(forms.ModelForm):
	def __init__(self, registration, *args, **kwargs):
		self.registration = registration
		
		if registration.user:
			pn_field = User._meta.get_field('phone_number').formfield()
			phone_number = registration.user.phone_number
		else:
			pn_field = Registration._meta.get_field('phone_number').formfield()
			phone_number = registration.phone_number
		
		try:
			instance = self._meta.model._default_manager.get(registration=registration)
		except ObjectDoesNotExist:
			instance = self._meta.model(registration=registration)
		kwargs['instance'] = instance
		
		super(HousingPhoneNumberForm, self).__init__(*args, **kwargs)
		self.fields['phone_number'] = pn_field
		self.initial.update({
			'phone_number': phone_number
		})
	
	def save(self, commit=True):
		if 'phone_number' in self.changed_data:
			if self.registration.user:
				self.registration.user.phone_number = self.cleaned_data['phone_number']
				self.registration.user.save()
			else:
				self.registration.phone_number = self.cleaned_data['phone_number']
				self.registration.save()
		instance = super(HousingPhoneNumberForm, self).save(commit=False)
		if commit:
			instance.save()
		return instance


class HousingOfferForm(HousingPhoneNumberForm):
	class Meta:
		model = HousingOffer
		exclude = ['coordinator', 'registration']


class HousingRequestForm(HousingPhoneNumberForm):
	class Meta:
		model = HousingRequest
		exclude = ['coordinator', 'registration', 'housed_with']


class CreateWorkshopForm(forms.ModelForm):
	def save(self, *args, **kwargs):
		instance = Workshop.objects.create_basic(name=self.cleaned_data['name'], tagline=self.cleaned_data['tagline'])
		instance.is_active = True
		return instance
	
	class Meta:
		model = Workshop
		fields = ['name', 'tagline']


WorkshopTrackInlineFormSet = forms.models.inlineformset_factory(Workshop, WorkshopTrack, extra=1)


class EditWorkshopForm(forms.ModelForm):
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


class WorkshopRegistrationForm(forms.ModelForm):
	person_type = forms.CharField(max_length=15, widget=forms.RadioSelect())
	housing = forms.CharField(max_length=1, widget=forms.RadioSelect(choices=HOUSING_CHOICES))
	waiver = forms.BooleanField(validators=[is_checked])
	
	def __init__(self, workshop, user=None, key=None, *args, **kwargs):
		self.user = user
		self.key = key
		self.workshop = workshop
		self.housing_form = None
		if user is None and key is None:
			instance = Registration(workshop=workshop)
		else:
			registration_kwargs = {'workshop': workshop}
			if user and not user.is_anonymous():
				registration_kwargs.update({'user': user})
			else:
				registration_kwargs.update({'key': key})
			
			try:
				instance = Registration.objects.get(**registration_kwargs)
				try:
					instance.housingoffer
				except:
					try:
						instance.housingrequest
					except:
						housing = NEUTRAL
					else:
						housing = REQUESTED
						self.housing_form = HousingRequestForm(instance, *args, **kwargs)
				else:
					housing = OFFERED
					self.housing_form = HousingOfferForm(instance, *args, **kwargs)
			except Registration.DoesNotExist:
				instance = Registration(**registration_kwargs)
			else:
				initial = {
					'price_option': instance.price.option.pk,
					'person_type': instance.price.person_type,
					# If they're registered, presumably they agreed to the waiver.
					'waiver': True,
					'housing': housing
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
			self.fields['first_name'] = instance._meta.get_field('first_name').formfield(required=True, initial=instance.first_name)
			self.fields['last_name'] = instance._meta.get_field('last_name').formfield(required=True, initial=instance.last_name)
			self.fields['email'] = instance._meta.get_field('email').formfield(required=True, initial=instance.email)
		else:
			self.fields['first_name'] = user._meta.get_field('first_name').formfield(required=True, initial=user.first_name)
			self.fields['last_name'] = user._meta.get_field('last_name').formfield(required=True, initial=user.last_name)
			self.fields['email'] = user._meta.get_field('email').formfield(required=True, initial=user.email)
	
	def clean(self):
		super(WorkshopRegistrationForm, self).clean()
		if self.housing_form:
			self.housing_form.full_clean()
			self._update_errors(self.housing_form.errors)
		return self.cleaned_data
	
	def save(self, commit=True):
		cleaned_data = self.cleaned_data
		
		self.instance.price = cleaned_data['price_option'].prices.get(person_type=cleaned_data['person_type'])
		instance = super(WorkshopRegistrationForm, self).save(commit=False)
		
		contact_fields = set(['first_name', 'last_name', 'email'])
		if contact_fields & set(cleaned_data.keys()) and contact_fields & set(self.changed_data):
			for field_name in contact_fields & set(cleaned_data.keys()):
				if instance.user is None:
					setattr(instance, field_name, cleaned_data[field_name])
				else:
					# TODO: Special-case user email setting to use the UserEmail stuff.
					setattr(instance.user, field_name, cleaned_data[field_name])
			if instance.user:
				instance.user.save()
		if self.key is None:
			instance.key = instance.make_key()
		if 'housing' in cleaned_data and 'housing' in self.changed_data:
			housing = cleaned_data['housing']
			
			if housing in [REQUESTED, OFFERED] and instance.pk is None:
				instance.save()
			
			if housing != REQUESTED:
				try:
					instance.housing_request
				except:
					pass
				else:
					instance.housing_request.delete()
			else:
				default_kwargs = {
					'registration': instance,
					'nonsmoking': False,
					'no_cats': False,
					'no_dogs': False,
				}
				HousingRequest.objects.create(**default_kwargs)
			if housing != OFFERED:
				try:
					instance.housing_offer
				except:
					pass
				else:
					instance.housing_offer.delete()
			else:
				default_kwargs = {
					'registration': instance,
					'smoking': False,
					'cats': False,
					'dogs': False,
				}
				HousingOffer.objects.create(**default_kwargs)
		elif self.housing_form:
			self.housing_form.save()
		if commit:
			instance.save()
		return instance
	
	class Meta:
		model = Registration
		fields = ['track', 'dancing_as']
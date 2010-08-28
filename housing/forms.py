from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from stepping_out.housing.models import OfferedHousing, RequestedHousing, HousingCoordinator


class OfferedHousingForm(ModelForm):
	phone_number = User._meta.get_field('phone_number').formfield()
	
	def __init__(self, user, event, *args, **kwargs):
		#if 'instance' in kwargs and kwargs['instance'] is not None:
		#	self.user = instance.user
		#	self.coordinator = instance.coordinator
		#	self.event = instance.coordinator.event
		#else:
		self.event = event
		self.user = user
		self.coordinator = HousingCoordinator.objects.get_or_create(event_content_type=ContentType.objects.get_for_model(event), event_object_id=event.id)[0]
		
		initial = {
			'phone_number': user.phone_number
		}
		initial.update(kwargs.get('initial', {}))
		kwargs['initial'] = initial
		
		try:
			instance = OfferedHousing.objects.get(user=user, coordinator=self.coordinator)
		except OfferedHousing.DoesNotExist:
			instance = OfferedHousing(user=user, coordinator=self.coordinator)
		kwargs['instance'] = instance
		super(OfferedHousingForm, self).__init__(*args, **kwargs)
	
	def save(self):
		self.user.phone_number = self.cleaned_data['phone_number']
		self.user.save()
		self.instance.save()
	
	class Meta:
		model = OfferedHousing
		exclude = ['coordinator', 'user']


class RequestedHousingForm(ModelForm):
	phone_number = User._meta.get_field('phone_number').formfield(required=True)
	
	def __init__(self, user, event, *args, **kwargs):
		self.event = event
		self.user = user
		self.coordinator = HousingCoordinator.objects.get_or_create(event_content_type=ContentType.objects.get_for_model(event), event_object_id=event.id)[0]
		
		initial = {
			'phone_number': user.phone_number
		}
		initial.update(kwargs.get('initial', {}))
		kwargs['initial'] = initial
		
		try:
			instance = RequestedHousing.objects.get(user=user, coordinator=self.coordinator)
		except RequestedHousing.DoesNotExist:
			instance = RequestedHousing(user=user, coordinator=self.coordinator)
		kwargs['instance'] = instance
		super(RequestedHousingForm, self).__init__(*args, **kwargs)
	
	def save(self):
		self.user.phone_number = self.cleaned_data['phone_number']
		self.user.save()
		self.instance.save()
	
	class Meta:
		model = RequestedHousing
		exclude = ['coordinator', 'user', 'housed_with']
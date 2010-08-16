from django.forms.models import ModelForm, BaseInlineFormSet, inlineformset_factory
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet, generic_inlineformset_factory
from stepping_out.pricing.models import PricePackage, PriceOption, Price


class PriceInlineFormSet(BaseInlineFormSet):
	pass


class PriceOptionInlineFormSet(BaseInlineFormSet):
	subformset = inlineformset_factory(PriceOption, Price, formset=PriceInlineFormSet)
	
	def __init__(self, *args, **kwargs):
		super(PriceOptionInlineFormSet, self).__init__(*args, **kwargs)
		self.subformset_instances = []
		for option in self.queryset:
			self.subformset_instances.append(self.subformset(instance=option))


class BasePricePackageFormSet(BaseGenericInlineFormSet):
	"""
	The model for this formset should always be price package. Can I enforce that?
	"""
	subformset = inlineformset_factory(PricePackage, PriceOption, formset=PriceOptionInlineFormSet)
	def __init__(self, *args, **kwargs):
		super(BasePricePackageFormSet, self).__init__(*args, **kwargs)
		self.subformset_instances = []
		for package in self.queryset:
			self.subformset_instances.append(self.subformset(instance=package))
PricePackageFormSet = generic_inlineformset_factory(
	model=PricePackage, formset=BasePricePackageFormSet, ct_field='event_content_type',
	fk_field='event_object_id')
from django.forms.models import ModelForm, BaseInlineFormSet, inlineformset_factory
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet, generic_inlineformset_factory
from stepping_out.pricing.models import PricePackage, PriceOption, Price
from stepping_out.pricing.people import registry


class PriceOptionForm(ModelForm):
	def save(self, commit=True):
		instance = super(PriceOptionForm, self).save(commit)
		
		if instance.pk:
			for person_type in instance.package.person_types:
				price = instance.prices.get_or_create(person_type=person_type)
				price.price = self.cleaned_data[person_type]
		return instance
	
	class Meta:
		model = PriceOption


class PriceOptionInlineFormSet(BaseInlineFormSet):
	def add_fields(self, form, index):
		super(PriceOptionInlineFormSet, self).add_fields(form, index)
		for person_type in self.instance.person_types:
			form.fields[person_type] = Price._meta.get_field('price').formfield(label=registry[person_type])
		
		if form.instance.pk:
			form.initial.update(dict(zip(self.instance.person_types, [price.price for price in form.instance.prices.all()])))


class BasePricePackageFormSet(BaseGenericInlineFormSet):
	"""
	The model for this formset should always be price package. Can I enforce that?
	"""
	subformset = inlineformset_factory(PricePackage, PriceOption, form=PriceOptionForm, formset=PriceOptionInlineFormSet, extra=1)
	
	def add_fields(self, form, index):
		super(BasePricePackageFormSet, self).add_fields(form, index)
		if form.instance.pk:
			form.subformset_instance = self.subformset(self.data, self.files, form.instance, prefix="%s_%s" % (self.prefix, index))
	
	def save(self, commit=True):
		for form in self.forms:
			if form.instance.pk:
				form.subformset_instance.save()
		return super(BasePricePackageFormSet, self).save(commit)


PricePackageFormSet = generic_inlineformset_factory(
	model=PricePackage, formset=BasePricePackageFormSet, ct_field='event_content_type',
	fk_field='event_object_id', extra=1)
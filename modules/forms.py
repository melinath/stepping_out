from django.forms.forms import BaseForm
from django.utils.datastructures import SortedDict
from stepping_out.modules.proxies import ProxyField


def get_declared_fields(bases, attrs, with_base_fields=True):
	fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, ProxyField)]
	fields.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))
	
	if with_base_fields:
		for base in bases[::-1]:
			if hasattr(base, 'base_fields'):
				fields = base.base_fields.items() + fields
	else:
		for base in bases[::-1]:
			if hasattr(base, 'declared_fields'):
				fields = base.declared_fields.items() + fields

	return SortedDict(fields)


def fields_for_patch(patch):
	return SortedDict([(f.name, f.formfield()) for f in patch._meta.field_proxies])


class PatchFormMetaclass(type):
	def __new__(cls, name, bases, attrs):
		try:
			parents = [b for b in bases if issubclass(b, PatchForm)]
		except NameError:
			# We are defining ProxyModelForm itself.
			parents = None
		
		new_class = super(PatchFormMetaclass, cls).__new__(cls, name, bases,
			attrs)
		if not parents:
			return new_class
		
		declared_fields = get_declared_fields(bases, attrs)
		patch = attrs.get('patch', None)
		if patch:
			# If there's a patch, extract fields from that.
			fields = fields_for_patch(patch)
			fields.update(declared_fields)
		else:
			fields = declared_fields
		new_class.declared_fields = declared_fields
		new_class.base_fields = fields
		return new_class


class PatchForm(BaseForm):
	__metaclass__ = PatchFormMetaclass
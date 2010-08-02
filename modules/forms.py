from django import forms
from django.utils.datastructures import SortedDict
from stepping_out.modules.fields import BaseProxyField, InlineField


def get_declared_fields(bases, attrs, with_base_fields=True):
	fields = []
	fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, BaseProxyField)]
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


def for_module(module):
	all_fields = SortedDict()
	fields = SortedDict()
	formsets = SortedDict()
	for field_proxy in module._meta.field_proxies:
		try:
			formsets[field_proxy.name] = all_fields[field_proxy.name] = field_proxy.formset
		except AttributeError:
			fields[field_proxy.name] = all_fields[field_proxy.name] = field_proxy.formfield()
	return all_fields, fields, formsets


class ModuleFormMetaclass(type):
	def __new__(cls, name, bases, attrs):
		try:
			parents = [b for b in bases if issubclass(b, ModuleForm)]
		except NameError:
			# We are defining ModuleForm itself.
			parents = None
		
		new_class = super(ModuleFormMetaclass, cls).__new__(cls, name, bases,
			attrs)
		if not parents:
			return new_class
		
		declared_fields = get_declared_fields(bases, attrs)
		module = attrs.get('module', None)
		if module:
			# If there's a module, extract fields from that.
			all_fields, fields, formsets = for_module(module)
			fields.update(declared_fields)
		else:
			fields = declared_fields
		
		new_class.all_fields = all_fields or fields
		new_class.formsets = formsets or {}
		new_class.declared_fields = declared_fields
		new_class.base_fields = fields
		return new_class


class ModuleForm(forms.BaseForm):
	__metaclass__ = ModuleFormMetaclass
	
	def __init__(self, module_instance, data=None, files=None, auto_id='id_%s',
				prefix=None, initial=None, error_class=forms.util.ErrorList,
				label_suffix='', empty_permitted=False):
		self._messages = []
		self.formset_instances = {}
		
		self.module_instance = module_instance
		module_data = dict([
			(f.name, f._get_val_from_obj(module_instance))
			for f in module_instance._meta.field_proxies if not isinstance(f, InlineField)
		])
		
		module_data.update(initial or {})
		
		defaults = {
			'initial': module_data,
			'data': data,
			'files': files,
			'auto_id': auto_id,
			'prefix': prefix,
			'error_class': error_class,
			'label_suffix': label_suffix,
			'empty_permitted': empty_permitted
		}
		super(ModuleForm, self).__init__(**defaults)
		for name, formset in self.formsets.items():
			self.formset_instances[name] = formset(data, files, module_instance.user
				)#initial=initial)) ??
	
	def is_valid(self):
		for formset in self.formset_instances.values():
			if not formset.is_valid():
				return False
		return super(ModuleForm, self).is_valid()
	
	def save(self):
		opts = self.module_instance._meta
		cleaned_data = self.cleaned_data
		for f in opts.field_proxies:
			if not f.name in cleaned_data:
				continue
			f.save_form_data(self.module_instance, cleaned_data[f.name])
		# need to put thing for formsets here.
		self.module_instance.save()
		
		for formset in self.formset_instances.values():
			formset.save()
	
	def add_message(self, level, msg):
		self._messages.append((level, msg))
	
	@property
	def messages(self):
		messages = self._messages
		for formset in self.formset_instances.values():
			messages.extend(formset.messages)
		return messages


def moduleform_factory(module_class, form_name=None, module_form=ModuleForm):
	if form_name is None:
		form_name = "%sModuleForm" % module_class.__name__
	
	attrs = {'module': module_class}
	
	return ModuleFormMetaclass(form_name, (module_form,), attrs)
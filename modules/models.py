from django.contrib.auth.models import User
from django.db.models import OneToOneField, ForeignKey, ManyToManyField


def _get_rel_fields(opts, types):
	if types == (ManyToManyField,):
		return opts.many_to_many
	elif ManyToManyField in types:
		return opts.fields + opts.many_to_many
	
	return opts.fields


def _get_rel(parent_model, model, related_name=None, types=(ForeignKey,)):
	opts = model._meta
	if related_name:
		# FIXME: what if there's no field?
		link = opts.get_field(related_name)
		if not isinstance(link, types) or \
				(link.rel.to != parent_model and
				 link.rel.to not in parent_model._meta.get_parent_list()):
			raise Exception("field '%s' is not a ForeignKey to %s" % (related_name, parent_model))
	else:
		links_to_parent = [
			f for f in _get_rel_fields(opts, types)
			if isinstance(f, types)
			and (f.rel.to == parent_model
				or f.rel.to in parent_model._meta.get_parent_list())
		]
		if len(links_to_parent) == 1:
			link = links_to_parent[0]
		elif len(links_to_parent) == 0:
			raise Exception("%s has no related fields to %s" % (model, parent_model))
		else:
			raise Exception("%s has more than one related field to %s" % (model, parent_model))
	return link


def flat_get_or_create(self, user):
	return self.model._default_manager.get_or_create(user=user)[0]


class ModelProxyMetaclass(type):
	def __new__(cls, name, bases, attrs):
		super_new = super(ModelProxyMetaclass, cls).__new__
		parents = [b for b in bases if isinstance(b, ModelProxyMetaclass)]
		if not parents:
			return super_new(cls, name, bases, attrs)
		
		module = attrs.pop('__module__')
		new_class = super_new(cls, name, bases, {'__module__': module})
		
		if 'model' not in attrs:
			raise AttributeError("Class %s does not define a model attribute." % name)
		
		new_class.model = attrs['model']
		
		if attrs['model'] != User:
			model = attrs['model']
			related_name = attrs.get('related_field_name', None)
			new_class.related_field_name = related_name
			
			new_class.link = link = _get_rel(
				User,
				model,
				related_name = related_name,
				types=(ForeignKey, OneToOneField, ManyToManyField)
			)
			
			if isinstance(link, OneToOneField) or \
					isinstance(link, ForeignKey) and link.unique:
				new_class._get_for_user = classmethod(flat_get_or_create)
			else:
				new_class._get_for_user = model._default_manager.filter
		return new_class


class ModelProxy(object):
	"""
	Subclasses must define a "model" attribute. They can also define a
	"related_field_name" attribute to specify the field on the model which
	relates to Users.
	"""
	__metaclass__ = ModelProxyMetaclass
	related_field_name = 'users'
	
	def __init__(self, user):
		self.user = user
		
		if self.model == User:
			self.for_user = user
		else:
			self.for_user = self._get_for_user(**{self.related_field_name: user})
	
	def save(self):
		try:
			for model in self.for_user:
				model.save()
		except TypeError:
			self.for_user.save()
	
	@classmethod
	def get_field(self, field_name):
		return self.model._meta.get_field(field_name)
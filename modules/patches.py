from django.forms.models import ModelForm, construct_instance


class Patch(object):
	# note: these forms are already initialized. I.e. they already have data from POST, if any.
	def __init__(self, instance):
		self.instance = instance
		self.forms = []
	
	def add_form(self, form):
		if not isinstance(form, ModelForm):
			raise TypeError("%s is not a ModelForm instance" % form)
		
		if form.instance != self.instance:
			raise TypeError("Patch only accepts forms related to %s" % self.instance)
		
		self.forms.append(form)
	
	def is_valid(self):
		for form in self.forms:
			if not form.is_valid():
				return False
		return True
	
	def save(self, *args, **kwargs):
		# FIXME: actually handle the arguments save could get?
		# FIXME: handle any errors that come up.
		
		for form in self.forms:
			self.instance = construct_instance(form, self.instance)
		self.instance.save()


class Weaver(object):
	def __init__(self, section, request):
		self.section = section
		self.request = request
		self.patches = {}
		self.classes = set()
		
		for module in section.modules:
			for form in module.get_forms(request):
				self.patch(form)
	
	def patch(self, form):
		if not isinstance(form, ModelForm):
			raise TypeError("%s is not a ModelForm instance" % form)
		
		instance = form.instance
		
		if instance is None:
			raise TypeError('NoneType cannot be patched')
		
		if instance not in self.patches:
			self.patches[instance] = Patch(instance)
		
		self.patches[instance].add_form(form)
	
	def is_valid(self, form):
		for patch in self.patches:
			if not patch.is_valid():
				return False
		return True
	
	def save(self, *args, **kwargs):
		for patch in self.patches:
			patch.save()
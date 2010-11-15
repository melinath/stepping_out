from django.utils.datastructures import SortedDict


class OrderedDict(SortedDict):
	"""
	A sorted dictionary that defines a sort method for ordering. It accepts args
	for the sorting function on init.
	"""
	def __init__(self, data=None, *args, **kwargs):
		self.sorting_args = (args, kwargs,)
	
	def sort(self):
		if getattr(self, 'sorted', False):
			return
		
		args, kwargs = self.sorting_args
		self.keyOrder = [k for k,v in sorted(self.raw_items(), *args, **kwargs)]
		self.sorted = True
	
	def __setitem__(self, key, value):
		if key not in self:
			self.keyOrder.append(key)
			self.sorted = False
		super(SortedDict, self).__setitem__(key, value)
	
	def __iter__(self):
		self.sort()
		return super(OrderedDict, self).__iter__()
	
	def raw_items(self):
		"For fetching the dict items for sorting."
		return super(SortedDict, self).items()
	
	def items(self):
		self.sort()
		return super(OrderedDict, self).items()
	
	def iteritems(self):
		self.sort()
		return super(OrderedDict, self).iteritems()
	
	def keys(self):
		self.sort()
		return super(OrderedDict, self).keys()
	
	def iterkeys(self):
		self.sort()
		return super(OrderedDict, self).iterkeys()
	
	def values(self):
		self.sort()
		return super(OrderedDict, self).values()
	
	def itervalues(self):
		self.sort()
		return super(OrderedDict, self).itervalues()
	
	def setdefault(self, key, default):
		if key not in self:
			self.keyOrder.append(key)
			self.sorted = False
		return super(SortedDict, self).setdefault(key, default)
	
	def value_for_index(self, index):
		self.sort()
		return super(OrderedDict, self).value_for_index(self, index)
	
	def insert(self, index, key, value):
		self.sorted = False
		super(OrderedDict, self).insert(index, key, value)
	
	def copy(self):
		obj = super(OrderedDict, self).copy()
		obj.sorted = self.sorted
		return obj
	
	def clear(self):
		super(OrderedDict, self).clear()
		self.sorted = True
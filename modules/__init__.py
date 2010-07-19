from stepping_out.modules import defaults
from stepping_out.modules.modules import Module, ModuleModel, ModuleMultiModel
from stepping_out.modules.sections import Section
from stepping_out.modules.sites import ModuleAdminSite, site


def autodiscover():
	"""
	Auto-discover INSTALLED_APPS modules.py modules and fail silently
	when not present. Forces an import on them to register any sections
	provided.
	"""
	
	import copy
	from django.conf import settings
	from django.utils.importlib import import_module
	from django.utils.module_loading import module_has_submodule
	
	for app in settings.INSTALLED_APPS:
		if __package__ == app:
			continue
		
		mod = import_module(app)
		
		# try importing the app's pipettes module
		try:
			before_import_registry = copy.copy(site._registry)
			import_module('%s.modules' % app)
		except:
			site._registry = before_import_registry
			if module_has_submodule(mod, 'modules'):
				raise
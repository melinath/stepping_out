from django.forms.models import modelform_factory
from stepping_out.admin.admin import ConfigurationModuleAdmin
from stepping_out.admin.modules import ConfigurationModule
from stepping_out.admin.sites import site
from stepping_out.contrib.workshops.forms import CreateWorkshopForm, EditWorkshopForm
from stepping_out.contrib.workshops.models import Workshop


class WorkshopModule(ConfigurationModule):
	model = Workshop
	slug = 'workshops'
	verbose_name = 'Manage Workshops'


class WorkshopModuleAdmin(ConfigurationModuleAdmin):
	order = 50
	create_form = CreateWorkshopForm
	edit_form = EditWorkshopForm
	edit_template = 'stepping_out/modules/config/workshops.html'


site.register(WorkshopModule, WorkshopModuleAdmin)
from django.conf.urls.defaults import patterns, url
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from stepping_out.admin.admin import QuerySetModuleAdmin
from stepping_out.admin.modules import QuerySetModule
from stepping_out.admin.sites import site
from stepping_out.contrib.workshops.forms import CreateWorkshopForm, EditWorkshopForm, WorkshopRegistrationForm
from stepping_out.contrib.workshops.models import Workshop, WorkshopUserMetaInfo
from stepping_out.housing import REQUESTED, OFFERED, RequestedHousing, OfferedHousing
from stepping_out.housing.forms import OfferedHousingForm, RequestedHousingForm
from stepping_out.pricing.modules import PaymentMixin


class WorkshopModule(QuerySetModule):
	model = Workshop
	slug = 'workshops'


class WorkshopModuleAdmin(QuerySetModuleAdmin, PaymentMixin):
	order = 50
	create_form = CreateWorkshopForm
	edit_form = EditWorkshopForm
	edit_template = 'stepping_out/modules/workshops/edit.html'
	registration_template = 'stepping_out/modules/workshops/registration.html'
	
	def has_permission(self, request):
		return request.user.is_active and request.user.is_authenticated()
	
	@property
	def urls(self):
		def wrap(view, cacheable=False):
			return self.admin_view(view, cacheable)
		
		urlpatterns = super(WorkshopModuleAdmin, self).urls + PaymentMixin.get_urls(self) + patterns('',
			url(r'^(?P<object_id>\d+)/register/$', wrap(self.register_view), name="%s_%s_register" % (self.admin_site.url_prefix, self.slug))
		)
		return urlpatterns
	
	def get_nav(self, request):
		if self.has_permission(request):
			info = (self.admin_site.url_prefix, self.slug)
			name, main_url, main_is_active, subnav = super(WorkshopModuleAdmin, self).get_nav(request)[0]
			
			model_is_active = False
			for instance in self.module_class.get_queryset():
				model_nav = ()
				if instance.registration_is_open:
					url = reverse('%s_%s_register' % info, kwargs={'object_id': instance.id})
					is_active = (url == request.path)
					if is_active:
						model_is_active = True
					model_nav += (
						('Register', url, is_active),
					)
					
					url = reverse('%s_%s_payment' % info, kwargs={'object_id': instance.id})
					is_active = (url == request.path)
					if is_active:
						model_is_active = True
					model_nav += (
						('Payment', url, is_active),
					)
				if model_nav:
					subnav += ((unicode(instance), None, is_active, model_nav),)
			
			if not subnav:
				return ()
			
			return ((name, main_url, main_is_active or model_is_active, subnav),)
		return ()
	
	def register_view(self, request, object_id):
		workshop = get_object_or_404(self.module_class.model, id=int(object_id))
		
		if request.method == 'POST':
			registration_form = WorkshopRegistrationForm(request.user, workshop, request.POST)
			offered_housing_form = OfferedHousingForm(request.user, workshop, request.POST)
			requested_housing_form = RequestedHousingForm(request.user, workshop, request.POST)
			
			if registration_form.is_valid():
				if registration_form.instance.pk:
					redirect_url = ''
					message = 'Changes saved.'
				else:
					redirect_url = reverse('%s_%s_payment' % (self.admin_site.url_prefix, self.slug), kwargs={'object_id': workshop.id})
					message = 'Your registration information has been processed.'
				
				if registration_form.cleaned_data['housing'] == REQUESTED:
					housing_form = requested_housing_form
					to_remove = OfferedHousing
				elif registration_form.cleaned_data['housing'] == OFFERED:
					housing_form = offered_housing_form
					to_remove = RequestedHousing
				else:
					registration_form.save()
					OfferedHousing.objects.filter(coordinator=workshop.housing, user=request.user).delete()
					RequestedHousing.objects.filter(coordinator=workshop.housing, user=request.user).delete()
					messages.add_message(request, messages.SUCCESS, message)
					return HttpResponseRedirect(redirect_url)
				
				if housing_form.is_valid():
					registration_form.save()
					housing_form.save()
					to_remove.objects.filter(coordinator=workshop.housing, user=request.user).delete()
					messages.add_message(request, messages.SUCCESS, message)
					return HttpResponseRedirect(redirect_url)
		else:
			registration_form = WorkshopRegistrationForm(request.user, workshop)
			offered_housing_form = OfferedHousingForm(request.user, workshop)
			requested_housing_form = RequestedHousingForm(request.user, workshop)
		
		context = self.get_context(request)
		context.update({
			'registration_form': registration_form,
			'offered_housing_form': offered_housing_form,
			'requested_housing_form': requested_housing_form
		})
		
		return render_to_response(self.registration_template, context, context_instance=RequestContext(request))
	
	def get_paypal_price(self, user, obj):
		return WorkshopUserMetaInfo.objects.get(user=user, workshop=obj).price.price


site.register(WorkshopModule, WorkshopModuleAdmin)
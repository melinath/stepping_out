from django.conf.urls.defaults import patterns, url
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from paypal.standard.forms import PayPalPaymentsForm
from stepping_out.pricing.processing import payment_hash


class PaymentMixin(object):
	"""
	Mixin for QuerySetModuleAdmin to add patterns and views for paypal ipn.
	"""
	payment_template = 'stepping_out/payment/payment.html'
	
	@property
	def urls(self):
		return self.get_urls()
	
	def get_urls(self):
		def wrap(view, cacheable=False):
			return self.admin_view(view, cacheable)
		
		urlpatterns = patterns('',
			url(r'^(?P<object_id>\d+)/payment/$', wrap(self.payment_view),
				name="%s_%s_payment" % (self.admin_site.url_prefix, self.slug)),
			url(r'^(?P<object_id>\d+)/payment/complete/$', wrap(self.payment_complete_view),
				name="%s_%s_payment_complete" % (self.admin_site.url_prefix, self.slug)),
			url(r'^(?P<object_id>\d+)/payment/cancel/$', wrap(self.payment_cancelled_view),
				name='%s_%s_payment_cancelled' % (self.admin_site.url_prefix, self.slug))
		)
		return urlpatterns
	
	def get_paypal_settings(self, request, obj):
		ct = ContentType.objects.get_for_model(obj)
		hash_args = [ct.app_label, ct.model, obj.id, request.user.id]
		hash = payment_hash(*hash_args)
		item_number = ':'.join(hash_args)
		return {
			'notify_url': reverse('paypal-ipn'),
			'cancel_return': reverse('%s_%s_payment_cancelled' % (self.admin_site.url_prefix, self.slug), kwargs={'object_id': obj.id}),
			'return_url': reverse('%s_%s_payment_complete' % (self.admin_site.url_prefix, self.slug), kwargs={'object_id': obj.id}),
			'custom': hash,
			'item_number': item_number,
			'item_name': unicode(obj)
		}
	
	def payment_view(self, request, object_id):
		obj = self.module_class.get_queryset().get(id=object_id)
		paypal_settings = self.get_paypal_settings(request, obj)
		form = PayPalPaymentsForm(initial=paypal_settings)
		context = self.get_context(request)
		context.update({'form': form})
		return render_to_response(self.payment_template, context, context_instance=RequestContext(request))
	
	def payment_complete_view(self, request, object_id):
		pass
	
	def payment_cancelled_view(self, request, object_id):
		pass
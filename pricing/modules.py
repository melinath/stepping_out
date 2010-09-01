from django.conf.urls.defaults import patterns, url
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from stepping_out.pricing.processing import payment_hash
from stepping_out.pricing.models import Payment


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
			url(r'^(?P<object_id>\d+)/payment/complete/$', csrf_exempt(wrap(self.payment_complete_view)),
				name="%s_%s_payment_complete" % (self.admin_site.url_prefix, self.slug)),
			url(r'^(?P<object_id>\d+)/payment/cancel/$', wrap(self.payment_cancelled_view),
				name='%s_%s_payment_cancelled' % (self.admin_site.url_prefix, self.slug))
		)
		return urlpatterns
	
	def get_paypal_settings(self, request, obj):
		ct = ContentType.objects.get_for_model(obj)
		hash_args = [ct.app_label, ct.model, unicode(obj.id), unicode(request.user.id)]
		hash = payment_hash(*hash_args)
		custom = ':'.join(hash_args)
		site = Site.objects.get_current()
		return {
			'notify_url': 'http://%s%s' % (site.domain, reverse('paypal-ipn')),
			'cancel_return': 'http://%s%s' % (site.domain, reverse('%s_%s_payment_cancelled' % (self.admin_site.url_prefix, self.slug), kwargs={'object_id': obj.id})),
			'return_url': 'http://%s%s' % (site.domain, reverse('%s_%s_payment_complete' % (self.admin_site.url_prefix, self.slug), kwargs={'object_id': obj.id})),
			'item_number': hash,
			'custom': custom,
			'item_name': unicode(obj),
			'amount': self.get_paypal_price(request, obj)
		}
	
	def payment_view(self, request, object_id):
		obj = self.module_class.get_queryset().get(id=object_id)
		paypal_settings = self.get_paypal_settings(request, obj)
		form = PayPalPaymentsForm(initial=paypal_settings)
		context = self.get_context(request)
		context.update({'form': form})
		return render_to_response(self.payment_template, context, context_instance=RequestContext(request))
	
	def payment_complete_view(self, request, object_id):
		try:
			hash_args = request.POST['custom'].split(':')
			hash = payment_hash(*hash_args)
			if hash != request.POST['item_number']:
				messages.add_message(request, messages.ERROR, 'The security data on this post was tampered with, but your payment may have been processed. Check back!')
			else:
				try:
					Payment.objects.get(ipn__txn_id=request.POST['txn_id'])
				except Payment.DoesNotExist:
					messages.add_message(request, messages.SUCCESS, "Paypal has processed your payment, but it hasn't quite reached our system yet. Check back!")
				else:
					messages.add_message(request, messages.SUCCESS, "We've received your payment. Thanks and we'll see you there!")
		except:
			pass
		
		return HttpResponseRedirect(reverse("%s_%s_payment" % (self.admin_site.url_prefix, self.slug), kwargs={'object_id': object_id}))
	
	def payment_cancelled_view(self, request, object_id):
		messages.add_message(request, messages.INFO, "Okay, your payment's been cancelled")
		return HttpResponseRedirect(reverse("%s_%s_payment" % (self.admin_site.url_prefix, self.slug), kwargs={'object_id': object_id}))
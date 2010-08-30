from paypal.standard.ipn.signals import payment_was_successful
from stepping_out.pricing.models import Payment
from django.utils.hashcompat import sha_constructor
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


def payment_hash(app_label, model, object_id, user_id):
	return sha_constructor(settings.SECRET_KEY + unicode(user_id) + unicode(object_id) +
		app_label + model).hexdigest()


def validate_item(ipn_obj):
	hash_args = ipn_obj.item_number.split(':')
	hash = payment_hash(*hash_args)
	if hash != ipn_obj.custom:
		return False
	return True


def process_payment(sender, **kwargs):
	ipn_obj = sender
	if validate_item(ipn_obj):
		app_label, model, object_id, user_id = ipn_obj.item_number.split(':')
		errors = False
		
		try:
			user = User.objects.get(id=user_id)
		except User.DoesNotExist:
			ipn_obj.set_flag("Payment attempted for user who does not exist: %s" % user_id)
			errors = True
		
		try:
			ct = ContentType.objects.get(app_label=app_label, model=model)
		except ContentType.DoesNotExist:
			ipn_obj.set_flag("Payment attempted for content type which does not exist: %s.%s" % (app_label, model))
			errors = True
		else:
			try:
				obj = ct.get_object_for_this_type(id=object_id)
			except ct.model_class().DoesNotExist:
				ipn_obj.set_flag("Payment attempted for %s with id %s which does not exist." % (ct.model_class().__name__, object_id))
				errors = True
		
		if not errors:
			payment = Payment(payment_for=obj, user=user, paid=ipn_obj.auth_amount, method='online')
			payment.save()
		else:
			ipn_obj.save()
	else:
		ipn_obj.set_flag("Security data does not match passthrough variables.")
		ipn_obj.save()
payment_was_successful.connect(process_payment)
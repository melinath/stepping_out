from paypal.standard.ipn.signals import payment_was_successful
from stepping_out.pricing.models import Payment
from django.utils.hashcompat import sha_constructor
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import datetime


def payment_hash(app_label, model, object_id, user_id):
	return sha_constructor(settings.SECRET_KEY + unicode(user_id) + unicode(object_id) +
		app_label + model).hexdigest()[::4]


def validate_item(ipn_obj):
	hash_args = ipn_obj.custom.split(':')
	hash = payment_hash(*hash_args)
	if hash != ipn_obj.item_number:
		return False
	return True


def process_payment(sender, **kwargs):
	ipn_obj = sender
	if validate_item(ipn_obj):
		app_label, model, object_id, user_id = ipn_obj.custom.split(':')
		
		try:
			user = User.objects.get(id=user_id)
		except User.DoesNotExist:
			ipn_obj.set_flag("Payment attempted for user who does not exist: %s" % user_id)
		
		try:
			ct = ContentType.objects.get(app_label=app_label, model=model)
		except ContentType.DoesNotExist:
			ipn_obj.set_flag("Payment attempted for content type which does not exist: %s.%s" % (app_label, model))
		else:
			try:
				obj = ct.get_object_for_this_type(id=object_id)
			except ct.model_class().DoesNotExist:
				ipn_obj.set_flag("Payment attempted for %s with id %s which does not exist." % (ct.model_class().__name__, object_id))
		
		# Should this process even if the ipn is flagged?
		if not ipn_obj.flag:
			payment = Payment(
				payment_for = obj,
				user = user,
				paid = ipn_obj.mc_gross,
				payment_method = 'online',
				payment_made = datetime.datetime.now(),
				ipn = ipn_obj
			)
			payment.save()
		else:
			ipn_obj.save()
	else:
		ipn_obj.set_flag("Security data does not match passthrough variables.")
		ipn_obj.save()
payment_was_successful.connect(process_payment)
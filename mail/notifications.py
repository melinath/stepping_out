from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site


def delivery_failure(msg):
	FAILED = msg.failed_delivery
	msg.log.error("Delivery failed at %s" % ', '.join(FAILED))
	body = """Hi there! Sorry to bother, but delivery of your message failed at the following addresses:
%s

The message you sent was:

%s
""" % ('\n'.join(FAILED), msg.as_string())
	send_mail('Delivery Failed: %s' % msg['subject'], body, settings.STEPPING_OUT_LISTADMIN_EMAIL, [msg.original_sender])


def permissions_failure(msg):
	FAILED = msg.rejected
	msg.log.error("Permissions error at %s" % ', '.join(FAILED))
	site = Site.objects.get_current()
	body = """Hi there! You've just tried to post to the following addresses:
%s

Unfortunately, you don't have permission to post to those addresses. If you
already have an account at %s, are you sure that this email address is attached
to it?

If you feel like this is an error, please email the webmaster.
--Mail Daemon

P.S. - the message you sent was:

%s
""" % ('\n'.join(FAILED), site.domain, msg.as_string())
	send_mail('Message rejected: %s' % msg['subject'], body, settings.STEPPING_OUT_LISTADMIN_EMAIL, [msg.original_sender])
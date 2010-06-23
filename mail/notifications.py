from django.core.mail import send_mail
from django.conf import settings


def delivery_failure(msg):
	body = """Hi there! Sorry to bother, but delivery of your message failed at the following addresses:
%s

The message you sent was:

%s
""" % ('\n'.join(msg.failed_delivery), msg.as_string())
	send_mail('Delivery Failed: %s' % msg['subject'], body, settings.STEPPING_OUT_LISTADMIN_EMAIL, [msg.original_sender])


def permissions_failure(msg):
	body = """Hi there! You've just tried to post to the following addresses:
%s

Unfortunately, you don't have permission to post to those addresses. Sorry!

If you feel like this is an error, please email the webmaster.
--Mail Daemon

P.S. - the message you sent was:

%s
""" % ('\n'.join(msg.rejected), msg.as_string())
	send_mail('Message rejected: %s' % msg['subject'], body, settings.STEPPING_OUT_LISTADMIN_EMAIL, [msg.original_sender])
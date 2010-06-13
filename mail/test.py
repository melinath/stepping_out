from cStringIO import StringIO
from django.conf import settings
from django.core.mail import send_mail, get_connection, EmailMessage
from django.core.mail.utils import DNS_NAME
from sys import stdout
import email
import smtplib

DEFAULTS = {
	'subject' : 'hello',
	'body' : 'This is a test, obviously.',
	'from_email' : 'from@test.test',
	'to' : ['to@test.test'] 
}

def django_get_test_message(subject=DEFAULTS['subject'], body=DEFAULTS['body'], from_email=DEFAULTS['from_email'], to=DEFAULTS['to']):
	return EmailMessage(subject, body, from_email, to)
	
	
def django_send_test_message(msg=django_get_test_message(), backend='console'):
	connection = get_connection(
		'django.core.mail.backends.%s.EmailBackend' % 'smtp',
		stream=stream
	)
	msg.send()


def python_get_test_message(subject=DEFAULTS['subject'], body=DEFAULTS['body'], from_email=DEFAULTS['from_email'], to=DEFAULTS['to']):
	msg = email.message.Message()
	msg.set_payload(body)
	msg['subject'] = subject
	msg['from'] = from_email
	msg['to'] = ','.join(to)
	return msg


def python_send_test_message(msg=python_get_test_message(), backend='console'):
	if backend == 'console':
		stdout.write(msg.as_string())
		return
	elif backend == 'smtp':
		connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, local_hostname=DNS_NAME.get_fqdn())
		connection.sendmail(msg['from'], msg['to'], msg.as_string())
		connection.quit()
	else:
		raise Exception('Unknown backend: %s' % backend)
from django.core.mail.utils import DNS_NAME
from django.db.models import Q
from django.contrib.auth.models import User
from models import MailingList
from sys import stdin
import email
import smtplib
from django.conf import settings


def route_email(input = stdin):
	"""
	Steps:
		1. parse the input
		2. get all the mailing lists the message is sent to.
		3. for each mailing list, send the message through to all users.
		   (but of course only if the sender has permission.)
	"""
	msg = parse_email(input)
	
	route_to_lists(msg)
	
	forward(msg)
		
	
def route_to_lists(msg):
	mailinglists = get_mailinglists(set(get_addrlist(msg, 'to')+get_addrlist(msg, 'cc')))
	
	bcc_set = set()
	
	for mailinglist in mailinglists:
		bcc_set |= get_user_emails(mailinglist.receivers())
	
	msg['bcc'] = ','.join(bcc_set)

def get_addrlist(msg, arg):
	addrlist = []
	try:
		for addr in msg.get_all(arg):
			if isinstance(addr, list):
				addrlist += addr
			elif isinstance(addr, str):
				addrlist.append(addr)
	except TypeError:
		pass
	return addrlist

def get_mailinglists(addrset):
	mailinglists = MailingList.objects.filter(address__in=set(addrset))
	return mailinglists

def parse_email(input):
	"""
	Given an input, parses it as a python Message object, Forget EmailMessage - just turns it back to a Message in the end anyway.
	"""
	input.seek(0)
	msg = email.message_from_file(input)
	return msg

def get_user_emails(userset):
	email_set = set()
	for user in userset:
		if user.email:
			email_set.add(user.email)
		
		email_set |= set(
			[email.email for email in user.useremail_set.filter(receives_email=True)]
		)
	
	return email_set

def users_from_email_list(emaillist):
	users = set(User.objects.filter(Q(useremail__email__in=emaillist)|Q(email__in=emaillist)))
	user_emails = set()
	for user in users:
		if user.email:
			user_emails.add(user.email)
			user_emails |= set([email.email for email in user.useremail_set.all()])
		
	remaining = set(emaillist)
	remaining -= user_emails
	
	return users, remaining


def forward(msg):
	connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, local_hostname=DNS_NAME.get_fqdn())
	connection.sendmail(msg['from'], msg['to'], msg.as_string())
	connection.quit()
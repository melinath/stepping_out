from django.core.mail.utils import DNS_NAME
from django.db.models import Q
from django.contrib.auth.models import User, AnonymousUser
from models import MailingList
from sys import stdin
import email
from email.parser import Parser
import smtplib
from django.conf import settings
from stepping_out.mail.message import SteppingOutMessage
from stepping_out.mail.notifications import delivery_failure, permissions_failure


MAX_SMTP_RECIPS = 99 # see http://people.dsv.su.se/~jpalme/ietf/mailing-list-behaviour.txt
"""
MAIL_LOG_PATH = '' #make sure this is writable by the mail server!
"""
# Perhaps make email domains an object with a foreignkey related to the site?

def route_email(input = stdin):
	"""
	Steps:
		1. parse the input
		2. get all the mailing lists the message is sent to.
		3. for each mailing list, send the message through to all users.
			(but of course only if the sender has permission.)

	New Step List:
		1. Receive message.
		2. parse to+cc fields
		   -- save the data as metadata somewhere on the message.
		3. check if there are any mailing lists matching to or cc addresses.
		   -- if not, bounce the message. raise an error?
		4. check if the sender matches one of the allowed posters.
		   -- if not, bounce the message.
		5. add the list headers - should have a custom function.
		6. forward the message.
	"""
	msg = parse_email(input)
	msg.parse_addrs()
	
	if settings.STEPPING_OUT_MAIL_LOG_PATH and settings.DEBUG_MAIL:
		# Really, it should always be *logged*, but this isn't what to log. I
		# should be logging things like "did it work?" and storing the messages
		# somewhere else like a database according to their id.
		fp = open(settings.STEPPING_OUT_MAIL_LOG_PATH, 'a')
		input.seek(0)
		fp.write(input.read())
		fp.write('\n\n\n')
	
	if msg.failed_delivery:
		delivery_failure(msg)
	
	if not msg.deliver_to:
		# Then do nothing.
		return
	
	# From here on, we know the mailing lists in question. The question is: who
	# is sending the message, and which mailing lists do they have permission to
	# send to? So: 1. What is the sending address? Could be envelope sender,
	# sender, from...
	
	
	# Is the email registered with a user? (Should I make it a list of possible
	# addresses?)
	try:
		user = User.objects.get(emails__email=msg.sender)
	except User.DoesNotExist:
		user = AnonymousUser()
	
	# Does the user have permission to post to each mailing list? If not, note.
	if not msg.can_post(user):
		permissions_failure(msg)
	
	if not msg.deliver_to or not msg.recips:
		# then they were all rejected for that user, or there are no recipients
		# for some other reason. Do nothing else.
		return
	
	recip_emails = get_user_emails(msg.recips)
	
	forward(msg, recip_emails)


def parse_email(input):
	"""
	Given an input, parses it as a python Message object, Forget EmailMessage -
	just turns it back to a Message in the end anyway.
	"""
	input.seek(0)
	msg = Parser(SteppingOutMessage).parse(input)
	return msg


def get_user_emails(userset):
	email_set = set()
	for user in userset:
		if user.email:
			email_set.add(user.email)
		
		#I'm not sure I want to let people receive email at more than one address...
		#email_set |= set(
		#	[email.email for email in user.emails.filter(receives_email=True)]
		#)
	
	return email_set


def forward(msg, recips):
	connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, local_hostname=DNS_NAME.get_fqdn())
	
	text = msg.as_string()
	
	# Really, this should be sent separately to each list so that the bounce is
	# correct, but for now, just pick a random list.
	env_sender_list = msg.data['addresses']['lists'].pop()
	env_sender = env_sender_list[1].address + '-bounce@' + env_sender_list[1].site.domain
	
	while len(recips) > MAX_SMTP_RECIPS:
		chunk = set(list(recips)[0:MAX_SMTP_RECIPS])
		connection.sendmail(env_sender, chunk, text)
		recips -= chunk
	
	connection.sendmail(env_sender, recips, text)
	connection.quit()
from stepping_out.mail.models import MailingList, UserEmail
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.hashcompat import sha_constructor
import datetime


def add_emails_to_list(mailing_list, emails):
	errors = []
	users = set()
	for email in emails:
		try:
			validate_email(email)
		except ValidationError, e:
			errors.append(e)
			continue
		
		try:
			user = User.objects.get(emails__email=email)
		except User.DoesNotExist:
			# Then make a new user with that email, a username, and a "random" password.
			username = email.split('@')[0]
			
			if User.objects.filter(username=username).count():
				username += sha_constructor(settings.SECRET_KEY + email + datetime.datetime.now().strftime('%Y/%m/%d %H:%S:%M')).hexdigest()[::4]
			
			password = sha_constructor(settings.SECRET_KEY + email + username + datetime.datetime.now().strftime('%Y/%m/%d %H:%S:%M')).hexdigest()[::3]
			user = User(email=email, username=username)
			user.set_password(password)
			user.save()
		
		users.add(user)
	
	for user in users:
		mailing_list.subscribed_users.add(user)
	
	mailing_list.save()
	
	return errors
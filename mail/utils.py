from stepping_out.mail.models import MailingList, UserEmail
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def add_emails_to_list(mailing_list, emails):
	errors = []
	for email in emails:
		try:
			validate_email(email)
		except ValidationError, e:
			errors.append(e)
			continue
		
		try:
			user = User.objects.get(emails__email=email)
			mailing_list.subscribed_users.add(user)
		except User.DoesNotExist:
			# Then add it as an unsorted address.
			useremail = UserEmail.objects.get_or_create(email=email)
			mailing_list.subscribed_emails.add(useremail)
	
	mailing_list.save()
	
	return errors
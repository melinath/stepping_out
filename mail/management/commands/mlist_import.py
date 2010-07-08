from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from stepping_out.mail.models import MailingList
from django.contrib.sites.models import Site
from optparse import make_option
from sys import stdin
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from cStringIO import StringIO


class Command(BaseCommand):
	help = 'Imports a file (or stdin) into a mailing list'
	args = '[-s <separator>] <listaddress> [<filename>]'
	
	option_list = BaseCommand.option_list + (
		make_option('-s', '--separator', dest='separator', default=',',
			help='Character(s) separating the email addresses. Default:","'),
	)
	
	def handle(self, *args, **options):
		if not args:
			raise CommandError('At least one argument must be given')
		
		email = args[0].partition('@')
		
		if email[1] == '':
			try:
				mlist = MailingList.objects.get(address=email[0])
			except MailingList.DoesNotExist:
				raise CommandError('No mailing list with address "%s" exists' % email[0])
			except MailingList.MultipleObjectsReturned:
				raise CommandError('Multiple lists begin with "%s". Please specify a full address.' % email[0])
		elif email[1] == '@' and len(email[2]) > 0:
			try:
				mlist = MailingList.objects.get(address=email[0], site__domain=email[2])
			except MailingList.DoesNotExist:
				mlist = MailingList(address=email[0])
				mlist.save()
				mlist.site, created = Site.objects.get_or_create(domain=email[2])
		else:
			raise CommandError('"%s" is not a valid email address.' % args[0])
		
		if len(args) == 1:
			fp = StringIO()
			fp.write(stdin.read())
			fp.seek(0)
		elif len(args) == 2:
			fp = open(args[1], 'r')
		else:
			raise CommandError('Too many arguments')
		
		invalid = []
		conflict = []
		
		for line in fp:
			emails = line.split(options['separator'])
			for email in emails:
				email = email.strip()
				try:
					validate_email(email)
				except ValidationError:
					if options['verbosity'] > 1:
						self.stderr.write('Invalid: %s\n' % email)
						invalid.append(email)
				else:
					try:
						user = User.objects.get(emails__email=email)
					except User.DoesNotExist:
						username = email.split('@')[0]
						user, created = User.objects.get_or_create(username=username)
						
						if not created:
							conflict.append(email)
							continue
						
						user.email = email
						user.save()
						user.emails.create(email=email)
					
					mlist.subscribed_users.add(user)
		
		if options['verbosity'] > 0:
			if invalid:
				if len(invalid) == 1:
					self.stdout.write('\nOne address was ')
				else:
					self.stdout.write('\n%d addresses were ' % len(invalid))
				
				self.stdout.write('invalid:\n%s\n' % ', '.join(invalid))
			
			if conflict:
				self.stdout.write('\nUsername conflicts were found when trying to make usernames for ')
				
				if len(conflict) == 1:
					self.stdout.write('one address:\n')
				else:
					self.stdout.write('%d addresses:\n' % len(conflict))
				
				self.stdout.write('%s\n\n' % ', '.join(conflict))
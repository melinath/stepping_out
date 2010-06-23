from email.message import Message
from stepping_out.mail.models import MailingList
from email.utils import getaddresses
import re
from email.header import Header
from email.message import Message
from django.conf import settings


ADMINISTRATIVE_KEYWORDS = ['bounce']
CONTINUATION_WS = '\t'
CONTINUATION = ',\n' + CONTINUATION_WS
COMMASPACE = ', '
MAXLINELEN = 78

# This is a list of all addresses owned by sites this script deals with.
# Ideally, it would be dynamically generated. Low priority, since I deliberately
# have no other addresses on the site.
OUR_ADDRESSES = [
	settings.STEPPING_OUT_LISTADMIN_EMAIL
]

nonascii = re.compile('[^\s!-~]')


def get_encoded_header(s):
	# I'm going to be a little more us-ascii-centric... right now, you can't set
	# the default charset for a list anyway, and I don't anticipate this being
	# that large of a project...
	charset = 'us-ascii'
	if nonascii.search(s):
		charset = 'iso-8859-1'
	return Header(s, charset)


class SteppingOutMessage(Message):
	"""
	This subclasses the default python email class. It contains a function to
	generate metadata based on its own contents to prepare it for shipping.
	Important! It doesn't ACT on the metadata. It only creates it.
	"""
	_metadata = {
		'original_sender': '',
		'recips': set(),
		'addresses': {
			'omit': set(),# set of (address, header) tuples that will be put back in place but not sent the message.
			'lists': set(), # set of (address, list, header) tuples for generating recips
			'fail': set(), # set of addresses that failed.
			'rejected': set() # set of (address, list, header) tuples for the lists that the user doesn't have permission to access.
		},
		'_addresses': False,
		'_sender': False
	}
	
	for kw in ADMINISTRATIVE_KEYWORDS:
		_metadata['addresses'][kw] = set()
	
	@property
	def original_sender(self):
		return self._metadata['original_sender']
	
	@property
	def failed_delivery(self):
		return self._metadata['addresses']['fail']
	
	@property
	def deliver_to(self):
		return self._metadata['addresses']['lists']
	
	@property
	def rejected(self):
		return self._metadata['addresses']['rejected']
	
	@property
	def recips(self):
		return self._metadata['recips']
	
	@property
	def sender(self):
		for h in ('from', 'from_', 'Reply-To', 'Sender'):
			if h == 'from_':
				hval = self.get_unixfrom()
			else:
				hval = self[h]
			if not hval:
				continue
			
			addrs = getaddresses([hval])
			try:
				realname, address = addrs[0]
				return address
			except IndexError:
				continue
		return ''

	def __getitem__(self, key):
		# Ensure that header values are unicodes.
		value = Message.__getitem__(self, key)
		if isinstance(value, str):
			return unicode(value, 'ascii')
		return value

	def get(self, name, failobj=None):
		# Ensure that header values are unicodes.
		value = Message.get(self, name, failobj)
		if isinstance(value, str):
			return unicode(value, 'ascii')
		return value
		
	
	def get_addr_set(self, arg):
		# return just the email address; drop the realname. Will patch in from
		# User object later.
		addresses = getaddresses(self.get_all(arg, []))
		return set([address[1] for address in addresses])
	
	def parse_addrs(self):
		self.get_sender_addr()
		self.parse_to_and_cc()
	
	def get_sender_addr(self):
		if self._metadata['_sender']:
			return
		
		self._metadata['original_sender'] = self.sender
		self._metadata['_sender'] = True
	
	def parse_to_and_cc(self):
		"""
		Check the original to and cc addresses to see if this message was even
		sent to a list. Split the addresses into:
			1. things to omit.
			2. things that are lists.
			3. things that are automated list functions
			4. things that fail to find a target.
			
		TODO: What about multiline address lists? Do I need to worry about unwrapping?
		Mailman comments claim a getaddresses bug...
		"""
		if self._metadata['_addresses']: #Then we were already here.
			return
		
		headers = ['to', 'cc', 'resent-to', 'resent-cc']
		mlists = MailingList.objects.by_domain()
		
		for header in headers: # so we put everything back right.
			addresses = self.get_addr_set(header)
			for address in addresses:
				name, domain = address.split('@')
				
				if domain not in mlists or (name, domain,) in OUR_ADDRESSES:
					# then it can't be a list! They'll get the message elsehow.
					self._metadata['addresses']['omit'].add((address, header))
					continue
				
				if name not in mlists[domain]:
					# Then it can't be a list, either. Unless it's administrative.
					namepart = name.rpartition('-')
					
					if namepart[2] in ADMINISTRATIVE_KEYWORDS and name != namepart[2] and namepart[0] in mlists[domain]:
						# It's an administrative thing!
						self._metadata['addresses'][namepart[2]].add((address, mlists[domain][namepart[0]], header))
					
					# it's not :-(
					self._metadata['addresses']['fail'].add(address)
					continue
				
				self._metadata['addresses']['lists'].add((address, mlists[domain][name], header))
		
		self._metadata['_addresses'] = True
	
	def cook_headers(self):
		"""
		Remove: DKIM
		"""
		list_addrs = set([tuple[1].full_address for tuple in self._metadata['addresses']['lists']])
		for addr in list_addrs:
			self['X-BeenThere'] = addr
		
		if 'precedence' not in self:
			self['Precedence'] = 'list'
		
		# Reply-To should be whatever it was plus whatever lists this is being sent to.
		reply_to = set([address[1] for address in getaddresses(self.get_all('reply-to', []) + [list_addrs])])
		del self['reply-to']
		if reply_to:
			msg['Reply-To'] = COMMASPACE.join(reply_to)
		
		# To and Cc should be able to stay the same... though we can also put things back
		# right if necessary.
		# The whole 'letting people send messages to multiple lists' thing is getting to me.
		# It causes problems. Like how do I set the list headers if it's going to
		# three different lists? 
		
		# Delete DKIM headers since they will not refer to our message.
		del msg['domainkey-signature']
		del msg['dkim-signature']
		del msg['authentication-results']
	
	def can_post(self, user):
		"""
		For each mailing list this message is being sent to, check if the user
		has permission to post to it. If so, add the list recipients to recips.
		If not, add the list to rejected.
		"""
		lists = self._metadata['addresses']['lists']
		rejected = self._metadata['addresses']['rejected']
		recips = self._metadata['recips']
		
		for mlist in lists:
			if mlist[1].can_post(user):
				recips |= mlist[1].recipients
			else:
				rejected.add(mlist)
		
		lists -= rejected
		self._metadata['recips'] = recips
		self._metadata['addresses'].update({'lists': lists, 'rejected': rejected})
		return not rejected
from django.core.mail import send_mail, get_connection, EmailMessage
from django.db.models import Q
from django.contrib.auth.models import User
from models import MailingList
from sys import stdout, stdin
import email
from cStringIO import StringIO

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
    
    msg.send()
        
    
def route_to_lists(msg):
    mailinglists = get_mailinglists(msg.to+msg.cc)
    
    bcc_set = set()
    
    for mailinglist in mailinglists:
        bcc_set |= get_user_emails(mailinglist.receivers())
    
    msg.bcc = list(bcc_set)

def get_mailinglists(addrset):
    mailinglists = MailingList.objects.filter(address__in=set(addrset))
    return mailinglists

def parse_email(input):
    """
    Given an input, parses it as a python Message object, then transforms this and
    returns it as a django EmailMessage object.
    Currently supports only simple text messages.
    """
    input.seek(0)
    msg = email.message_from_file(input)
    headers = {}
    for header in msg._headers:
        if header[0] in ['From', 'To', 'CC']:
            continue
        headers[header[0]] = header[1]
    
    def get_addrlist(arg):
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
    
    to_list = get_addrlist('to')
    cc_list = get_addrlist('cc')
            
    emsg = EmailMessage(
        subject = msg['subject'],
        body = msg.get_payload(),
        from_email = msg['from'],
        to = to_list,
        headers = headers
    )
    emsg.extra_headers['CC'] = ','.join(cc_list)
    emsg.cc = cc_list
    return emsg

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
"""
def add_bcc(message, mailinglist):
    
    Intelligently? adds the BCC to a django EmailMessage.
    I'm not sure if this is necessary... or a good idea.
    
    to_users, to_emails = users_from_emaillist(message.to)
    try:
        cc_users, cc_emails = users_from_emaillist(message.headers['Cc'].split(','))
    except KeyError:
        cc_users = set()
        cc_emails = set()
    bcc = get_user_emails(mailinglist.receivers())
    bcc -= to_users | cc_users
    
    message.bcc = list(bcc)
    return message
"""


def get_test_message():
    fp = StringIO()
    send_test_message(fp)
    return fp
    
def send_test_message(stream=stdout):
    connection = get_connection(
        'django.core.mail.backends.console.EmailBackend',
        stream=stream
    )
    send_mail(
        'Test email',
        'This is a test, obviously',
        'from@test.test',
        ['to@test.test'],
        connection=connection
    )
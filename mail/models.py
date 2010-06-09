from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

class UserList(models.Model):
    "Still need validation"
    name = models.CharField(max_length = 50)
    content_type = models.ForeignKey(ContentType)
    manager = models.CharField(
        max_length=30,
        help_text = "The manager's method must return a set of users. Default manager: objects.",
        blank = True
    )
    method = models.CharField(
        max_length=30,
        help_text = "The manager's method must return a set of users. Default method: all",
        blank = True
    )
    arg = models.CharField(
        max_length=30,
        blank = True,
        help_text = "The manager method may take a single string argument."
    )
    
    def __unicode__(self):
        return self.name
        
    def compile(self):
        model = self.content_type.model_class()
        manager = self.manager or u'objects'
        method = self.method or u'all'
        arg = self.arg
        
        function = model.__dict__[manager].manager.__getattribute__(method)
        
        if arg:
            return function(arg)
        else:
            return function()
            

class MailingList(models.Model):
    """
    This model should contain the options for each mailing list.
    """
    name = models.CharField(max_length=50)
    address = models.EmailField(max_length=100)
    
    subscribed_users = models.ManyToManyField(
        User,
        related_name = 'subscribed_mailinglist_set',
        blank = True,
        null = True
    )
    subscribed_groups = models.ManyToManyField(
        Group,
        related_name = 'subscribed_mailinglist_set',
        blank = True,
        null = True
    )
    subscribed_userlists = models.ManyToManyField(
        UserList,
        related_name = 'subscribed_mailinglist_set',
        blank = True,
        null = True
    )
    
    subscribers_may_post = models.BooleanField()
    nonsubscribers_may_post = models.BooleanField()
    self_subscribe_enabled = models.BooleanField(verbose_name = 'self-subscribe enabled')
    
    moderator_users = models.ManyToManyField(
        User,
        related_name='moderated_mailinglist_set',
        blank = True,
        null = True
    )
    moderator_groups = models.ManyToManyField(
        Group,
        related_name='moderated_mailinglist_set',
        blank = True,
        null = True
    )
    moderator_userlists = models.ManyToManyField(
        UserList,
        related_name='moderated_mailinglist_set',
        blank = True,
        null = True
    )
    
    def __unicode__(self):
        return self.name
    
    def remove_user(self, user):
        """
        user should be a user instance. This will take a user off the list.
        Is this actually useful?
        """
        pass
    
    def add_user(self, user):
        """
        user should be a user instance. This will add a user to the list.
        """
        pass
    
    def subscribers(self):
        return self.get_user_set('subscribed')
        
    def moderators(self):
        return self.get_user_set('moderator')
        
    def receivers(self):
        receivers = self.subscribers()
        receivers |= self.moderators()
        return receivers
        
    def get_user_set(self, prefix):
        
        userset = set(getattr(self, '%s_users' % prefix).all())
        for group in getattr(self, '%s_groups' % prefix).all():
            userset |= set(group.user_set.all())
            
        for userlist in getattr(self, '%s_userlists' % prefix).all():
            userset |= set(userlist.compile())
            
        return userset
        
    def user_may_post(self, user):
        try:
            if self.nonsubscribers_may_post:
                return True
                
            if self.subscribers_may_post and user in self.subscribers():
                return True
            
            if user in self.moderators():
                return True
        except:
            pass
        
        return False
    
    def posters(self):
        if self.nonsubscribers_may_post:
            return True
        
        posters = self.moderators()
        
        if self.subscribers_may_post:
            posters |= self.subscribers()
            
        return posters
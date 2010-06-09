from django.db import models
from django import forms

class Category(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children'
    )
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural='categories'
        ordering = ('name',)
    
    def parent_name(self):
        try:
            return self.parent.name
        except:
            return self.parent
    parent_name.admin_order_field = 'parent'
    
    def path(self):
        if self.parent:
            return '%s // %s' % (self.parent.__unicode__(), self.name,)
        
        return self.name
    
    def __unicode__(self):
        return self.path()
    
    def check_parentage(self):
        parent = self.parent
        while parent:
            if parent == self:
                raise Exception("A category can't be its own parent!")
            parent = parent.parent
    
    def save(self):
        self.check_parentage()
        super(Category, self).save()

class Link(models.Model):
    uid = models.CharField(max_length=200, editable=False)
    url = models.URLField(max_length=200)
    name = models.CharField(max_length=50)
    
    created = models.DateTimeField(auto_now_add = True)
    last_modified = models.DateTimeField(auto_now = True)
    
    categories = models.ManyToManyField(Category, through='LinkMetaInfo')
    
    def __unicode__(self):
        return self.name

class LinkMetaInfo(models.Model):
    """
    A link can be part of many categories and each category can contain many links.
    However, within each link it can only be part of one subcategory and it can
    only have one help text. So, part of the through field.
    More efficient to choose the lowest level and then just have it be added
    to each parent automatically. No - leaf model! Just add it to the lowest
    category.
    """
    link = models.ForeignKey(Link)
    category = models.ForeignKey(Category)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        return '%s: %s' % (self.category.__unicode__(), self.link.__unicode__())

"""
Each link should have:
1. A link id, some sort of hash of variables.
2. The link URL
3. The link name
4. created date
5. last modified date
6. meta information... i.e. regional information for clubs = through
7. Link help text/info text - what is the link for? i.e. yehoodi desc.
   -- This should be in a through db with category.
8. Category - Manytomany through.

This module should let people access a raw list of links: id and last-modified.
People can add linksyncs as another model. One's own list of links could be
compared against the raw list and synced according to most recent modified date.
Or, people can get a list of changes and approve/disapprove each change.

Save effort compiling link lists.

Really though you'd want each server to identify itself when requesting a link
sync, so that it could theoretically be added to the list of sites that server
also sends sync requests to.

Also, even deleted links should be kept in the database - that's a sync change,
after all. 'Active' vs 'inactive'.
"""
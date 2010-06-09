from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField
from django.contrib.contenttypes.models import ContentType
from settings import DEFAULT_STATE, DEFAULT_ZIP, DEFAULT_CITY
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Q
import datetime
from durationfield.db.models.fields.duration import DurationField
                                 
class Calendar(models.Model):
    """
    A calendar has a name.
    """
    name = models.CharField(max_length = 40, unique=True)
    
    def __unicode__(self):
        try:
            name = self.localcalendar.__unicode__()
            caltype = 'Local'
        except:
            try:
                name = self.externalcalendar.__unicode__()
                caltype = 'External'
            except:
                return self.name
        
        return '%s (%s)' % (name, caltype)

class LocalCalendar(Calendar):
    """
    No extra features for local calendars.
    """

    def __unicode__(self):
        return self.name

class ExternalCalendar(Calendar):
    """
    An external calendar has additionally a valid ics url and a 'last-checked'
    field which can't be edited. Eventually, add an admin action to 'check now':
    otherwise, check every half hour or so (if loaded.)
    
    Can I make it check automatically if it's saved?    
    """
    
    url = models.URLField(
        help_text = 'Valid URL of an ics (ICal) file'
    )
    last_checked = models.DateTimeField(blank=True, null=True, editable=True)
    prodid = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

class Building(models.Model):
    """
    A building may have a name. It will always have an address, city, state,
    and zip. (The zip code is necessary for determining nearby-ness... if
    I end up using it that way.)
    """
    name = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50, default=DEFAULT_CITY)
    state = USStateField(default=DEFAULT_STATE)
    zipcode = models.PositiveIntegerField(default=DEFAULT_ZIP)
    
    def name_or_address(self):
        return self.name or self.address
    name_or_address.short_description = 'building'
    
    def __unicode__(self):
        return '%s, %s %s' % (self.name_or_address(), self.city, self.state,)

class Venue(models.Model):
    """
    Venues have a name and are in a building. They may optionally specify
    where in the building.
    Venues may be displayed or not (is this really necessary? Otherwise, what
    criteria would I use to decide whether to display them?)
    """
    name = models.CharField(max_length=50)
    location = models.CharField(
        max_length=50,
        help_text = 'Where in the building?',
        blank = True
    )
    building = models.ForeignKey(Building)
    display = models.BooleanField()
    
    def __unicode__(self):
        return self.name

class CalItem(models.Model):
    """
    Basic model. Shouldn't be used to create items, but can be used to pull
    all of them easily.
    All items have a name, description, and time (i.e. start-time), and each
    is associated with one or more calendars.
    """
    name = models.CharField(max_length = 70)
    description = models.TextField()
    date = models.DateField(help_text='YYYY-MM-DD')
    
    UID = models.CharField(max_length=200, editable=False)
    
    last_modified = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)
    
    type = models.ForeignKey(ContentType, editable=False)
    
    calendars = models.ManyToManyField(
        LocalCalendar,
        blank=True,
        null=True
    )
    external_calendar = models.ForeignKey(
        ExternalCalendar,
        blank=True,
        null=True,
        editable = False
    )
    
    def __unicode__(self):
        return self.name
        
    def save(self, force_insert=False, force_update=False):
        if self.type_id == None:
            self.type = ContentType.objects.get_for_model(self.__class__)
        
        if not self.UID:
            self.UID = datetime.datetime.now().isoformat() + '//oswing.org'
            
        super(CalItem,self).save(force_insert, force_update)
    
    def get_instance(self):
        return self.type.get_object_for_this_type(id=self.id)
        
    def set_ical_description(self, item):
        item.add('description').value = self.description
        
    def set_ical_item(self, item):
        self.set_ical_description(item)
        item.add('summary').value = self.name
        item.add('created').value = self.created
        item.add('last-modified').value = self.last_modified
        item.add('dtstart').value = self.time
        item.add('uid').value = self.UID
        
        categories = [self.__class__.__name__.upper()]+\
            list(calendar.name.upper() for calendar in self.calendars.all())
        
        if self.external_calendar is not None:
            categories += [self.external_calendar.name.upper()]
        
        item.add('categories').value = categories
        
    def add_to_cal(self, ical):
        self.set_ical_item(ical.add('vevent'))

class CalItemChild(CalItem):
    "Necessary to have uniform access to the child class."
    class Meta:
        abstract = True
        
    parent = models.OneToOneField(
        CalItem,
        parent_link=True
    )

class Deadline(CalItemChild):
    """
    Sets itself as a VTODO instead of a VEVENT.
    Seems to make more sense.
    
    Should have a generic relationship to a workshop or ... (meeting?)
    """
    
    time = models.TimeField(blank=True, null=True, help_text='HH:MM:SS')
    
    def add_to_cal(self, ical):
        self.set_ical_item(ical.add('vtodo'))
        
    def set_ical_item(self, item):
        item.add('due').value = self.time
        super(Deadline, self).set_ical_item(item)

def set_ical_child(item, uid):
    child = item.add('related-to')
    child.value = uid
    child.params = {'RELTYPE' : ['CHILD']}
    
def set_ical_parent(item, uid):
    item.add('related-to').value = uid

class Workshop(CalItemChild):
    """
    Unlike any other event, a Workshop is assumed to be multi-day and have
    sub-events and a website. The relationships would be (set up) from the
    event side, though. Perhaps make a formfield someday to assign in the
    other direction?
    """
    end_date = models.DateField(verbose_name='end date')
    website = models.URLField()
    city = models.CharField(max_length=50, default='Oberlin')
    state = USStateField(default='OH')
    zipcode = models.CharField(max_length=12, default='44074')
    
    def set_ical_location(self, item):
        # location could have alternate representation as a vcard
        item.add('location').value = '%s %s' % (
            self.city,
            self.state,
        )
    
    def set_ical_children(self, item):
        for lesson in self.lesson_set.all():
            set_ical_child(item, lesson.UID)
        
        for dance in self.dance_set.all():
            set_ical_child(item, dance.UID)
        
    def set_ical_item(self, item):
        item.add('dtend').value = self.end
        item.add('url').value = self.website
        
        self.set_ical_children(item)
        self.set_ical_location(item)
        
        super(Workshop, self).set_ical_item(item)
        

class CalEvent(CalItemChild):
    """
    Abstract class containing items common to all event-type items.
    length should be validated as always positive or -1.
    """
    time = models.TimeField(help_text='HH:MM:SS')
    
    venue = models.ForeignKey(Venue)
    length = DurationField(help_text='Example: 4d 3h 22m')
    
    def set_ical_location(self, item):
        # location could have alternate representation as a vcard
        item.add('location').value = '%s\r\n %s\r\n %s %s' % (
            self.venue.name,
            self.venue.building.name_or_address(),
            self.venue.building.city,
            self.venue.building.state,
        )
    
    def set_ical_item(self, item):
        self.set_ical_location(item)
        self.set_ical_child(item)
        self.set_ical_parent(item)
        super(CalEvent, self).set_ical_item(item)
    
    def set_ical_child(self, item):
        pass
    def set_ical_parent(self, item):
        pass
    
    class Meta:
        abstract = True

class Dance(CalEvent):
    """
    A dance can optionally be associated with a workshop or a single class.
    """
    lesson = models.OneToOneField(
        'Lesson',
        blank=True,
        null=True,
        help_text = 'Pre-dance lesson'
    )
    workshop = models.ForeignKey(
        Workshop,
        blank=True,
        null = True,
        help_text = 'Workshop the dance is part of'
    )
    
    def set_ical_child(self, item):
        set_ical_child(item, self.lesson.UID)
        
    def set_ical_parent(self, item):
        set_ical_parent(item, self.workshop.UID)
    
class Lesson(CalEvent):
    """
    A lesson has a name, teachers, and a difficulty level. Can optionally
    be associated with a workshop. Could have a cost field defaulting to free,
    but how would I represent that in the database?
    """
    teachers = models.ManyToManyField(User, blank=True, null=True)
    difficulty = models.CharField(max_length = 20, blank=True)
    workshop = models.ForeignKey(Workshop, blank=True, null=True)
    #cost = ??? How to represent this ??? XML?
    
    def set_ical_parent(self, item):
        try:
            set_ical_parent(item, self.workshop.uid)
        except:
            pass
        
        try:
            set_ical_parent(item, self.dance.uid)
        except:
            pass
        
    def set_ical_teachers(self, item):
        for teacher in self.teachers.all():
            new_teacher = item.add('attendee')
            #new_teacher.value = 
            new_teacher.params = {
                'ROLE': ['TEACHER'],
                'CN' : [teacher.get_full_name()]
            }
    
    def set_ical_item(self, item):
        self.set_ical_teachers(item)
        super(Lesson, self).set_ical_item(item)
    
class Meeting(CalEvent):
    """
    A meeting has an agenda and minutes. A textfield seems intuitively the
    correct choice for the agenda, though technically an agenda is a number of
    items which could be stored in a database...
    """
    agenda = models.TextField(blank=True)
    minutes = models.TextField(blank=True)
    


class Ride(models.Model):
    """
    A ride includes the person giving the ride, the people taking the ride,
    the number of seats offered, and optionally a meeting time/place.
    """
    ride_giver = models.ForeignKey(User, related_name='giving_ride_set')
    ride_takers = models.ManyToManyField(User, related_name='taking_ride_set')
    seats = models.PositiveIntegerField()
    
    time = models.DateTimeField(blank=True)
    place = models.CharField(max_length=100, blank=True)
    
    """
    A ride can only be offered to a class, workshop, or dance.
    """
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to = Q(model='class') | Q(model='workshop') | Q(model='dance'),
        verbose_name='event type'
    )
    object_id = models.PositiveIntegerField(verbose_name='event id')
    event = generic.GenericForeignKey()
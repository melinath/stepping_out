import vobject
import datetime
from django.http import HttpResponse
from stepping_out.contrib.calendar.models import CalItem, LocalCalendar, ExternalCalendar
from django.shortcuts import render_to_response

def get_calendar_events(
    calendar_key = None,
    manager_key = 'calitem_set',
    itemfilter = None,
    range_start = datetime.date.today(),
    range = datetime.timedelta(28)
    ):
    try:
        try:
            calendar = LocalCalendar.objects.get(name = calendar_key)
        except:
            calendar = ExternalCalendar.objects.get(name = calendar_key)
        
        manager = getattr(calendar, manager_key)
    except:
        calendar = None
        manager = CalItem.objects

    try:
        itemlist = manager.filter(itemfilter)
    except:
        itemlist = manager.all()

    return calendar, itemlist

def ical(request,
    calendar_key = None,
    itemfilter = None,
    manager_key='calitem_set'
    ):
    ical = vobject.iCalendar()
    
    calendar, itemlist = get_calendar_events(calendar_key, manager_key, itemfilter)
    
    try:
        ical.add('prodid').value = calendar.prodid
    except:
        if calendar == None:
            name = 'All'
        else:
            name = calendar.name
        
        ical.add('prodid').value=\
            '-//Oberlin Swing Society//Public iCalendar Export//%s' % name
    
    for item in itemlist:
        item = item.get_instance()
        item.add_to_cal(ical)
        
    icalstream = ical.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    
    return response
    
def calendar_widget_context(dayend):
    class DayNode:
        def __init__(self, date, viewed = False, contains = False):
            self.date = date
            self.viewed = viewed
            self.contains = contains
    
    class MonthNode:
        def __init__(self, month):
            self.name = month
    
    def get_or_populate(key1, key2, default):
        try:
            return request.session[key1][key2]
        except KeyError:
            return default
            try:
                request.session[key1][key2] = default
            except KeyError:
                request.session[key1] = { key2 : default }
                
    start = get_or_populate('calendar', 'widget_start', datetime.datetime.now())
    days = 28
    month = start.month #to_string!
    
    month_events = CalItem.objects.exclude(
        date__gt = (start + datetime.timedelta(days))
    )
    
    nodelist = [MonthNode(start.month)]
    
    for day in [start+datetime.timedelta(delta) for delta in range(days+1)]:
        nodelist.append(DayNode(day.date()))
        
    return { 'daylist' : [] }

def calendar_widget(
        request,
        template = 'calendar_widget.template',
        dayend = 6
    ):
    """
    Given a request, this function returns the array needed for a calendar
    widget: a list of date and month nodes.
        1. day nodes. Contain:
            - whether the date is in the user's currently viewed range
            - whether the date contains any events. (This means concretely: any
              events that either start within the day or end after 6am
              (controlled by dayend variable)
            - date number (i.e. 1-31)
              
        2. month nodes. Contain:
            - Month name
    """
    
    return render_to_response(
        template,
        calendar_widget_context(),
        RequestContext(request)
    )

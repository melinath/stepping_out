from django.conf.urls.defaults import *
from stepping_out.contrib.calendar.views import ical

urlpatterns = patterns('',
    (r'^(?:ics|ical)/$', ical),
)

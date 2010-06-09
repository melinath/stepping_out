from django.conf.urls.defaults import *
from views import ical

urlpatterns = patterns('',
    (r'^(?:ics|ical)/$', ical),
)

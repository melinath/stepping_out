from django.conf import settings

DEFAULT_CITY = getattr(settings, 'SWINGTIME_DEFAULT_CITY', '')
DEFAULT_STATE = getattr(settings, 'SWINGTIME_DEFAULT_STATE', '')
DEFAULT_ZIP = getattr(settings, 'SWINGTIME_DEFAULT_ZIP', '')

"""
There should also be a profile for setting mailing lists, perhaps?
"""
IMPORTED_USER_INLINES = []
IMPORTED_GROUP_INLINES = []

from stepping_out.workshops.admin import USER_INLINES
IMPORTED_USER_INLINES += USER_INLINES

"""
from stepping_out.mail.admin import USER_INLINES, GROUP_INLINES
IMPORTED_USER_INLINES += USER_INLINES
IMPORTED_GROUP_INLINES += GROUP_INLINES
"""
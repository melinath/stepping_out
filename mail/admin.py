from django.contrib import admin
from django import forms
from models import MailingList, UserList


COLLAPSE_OPEN_CLASSES = ('collapse', 'open', 'collapse-open',)


class MailingListAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'address',
        'who_can_post',
        'self_subscribe_enabled'
    )
    list_filter = list_editable = (
        'who_can_post',
        'self_subscribe_enabled'
    )
    filter_horizontal = (
        'subscribed_users',
        'subscribed_groups',
        'subscribed_userlists',
        'moderator_users',
        'moderator_groups',
        'moderator_userlists'
    )
    fieldsets = (
        (None, {
            'fields' : (
                'name',
                'address',
                'site',
            )
        }),
        ('Options', {
            'fields' : (
                'who_can_post',
                'self_subscribe_enabled'
            )
        }),
        ('Subscribers', {
            'fields' : (
                'subscribed_users',
                'subscribed_groups',
                'subscribed_userlists',
            ),
            'classes': COLLAPSE_OPEN_CLASSES
        }),
        ('Moderators', {
            'fields' : (
                'moderator_users',
                'moderator_groups',
                'moderator_userlists'
            ),
            'classes': COLLAPSE_OPEN_CLASSES
        })
    )
    radio_fields = {'who_can_post':admin.VERTICAL}
    prepopulated_fields = {'address': ('name',)}

"""
class MailingListInline(admin.TabularInline):
    model = MailingList
    filter_horizontal = ['mailing_lists']

USER_INLINES = [MailingListInline,]
GROUP_INLINES = [MailingListInline,]
"""
admin.site.register(MailingList, MailingListAdmin)
admin.site.register(UserList)
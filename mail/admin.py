from django.contrib import admin
from django import forms
from models import MailingList, UserList

class MailingListAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'address',
        'subscribers_may_post',
        'nonsubscribers_may_post',
        'self_subscribe_enabled'
    )
    list_filter = list_editable = (
        'subscribers_may_post',
        'nonsubscribers_may_post',
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
            )
        }),
        ('Options', {
            'fields' : (
                'subscribers_may_post',
                'nonsubscribers_may_post',
                'self_subscribe_enabled'
            )
        }),
        ('Subscribers', {
            'fields' : (
                'subscribed_users',
                'subscribed_groups',
                'subscribed_userlists',
            ),
            'classes': ('collapse-open',)
        }),
        ('Moderators', {
            'fields' : (
                'moderator_users',
                'moderator_groups',
                'moderator_userlists'
            ),
            'classes': ('collapse-open',)
        })
    )

"""
class MailingListInline(admin.TabularInline):
    model = MailingList
    filter_horizontal = ['mailing_lists']

USER_INLINES = [MailingListInline,]
GROUP_INLINES = [MailingListInline,]
"""
admin.site.register(MailingList, MailingListAdmin)
admin.site.register(UserList)
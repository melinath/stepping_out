from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.shortcuts import get_object_or_404
from stepping_out.admin.admin import FormAdminSection
from stepping_out.admin.sites import site
from stepping_out.events.forms import EditEventForm
from stepping_out.events.models import *


class BuildingAdmin(admin.ModelAdmin):
	pass


class VenueAdmin(admin.ModelAdmin):
	pass


class EventNoteInline(admin.TabularInline):
	model = EventNote
	extra = 1


class EventInline(admin.StackedInline):
	fieldsets = (
		(None, {
			'fields': ('title', 'description', 'venue')
		}),
		('Times', {
			'fields': ('start_date', 'start_time', 'end_date', 'end_time')
		}),
		('Advanced', {
			'fields': ('parent_event', 'uid')
		})
	)
	verbose_name_plural = 'child events'
	verbose_name = 'child event'
	model = Event
	extra = 1
	classes = 'collapse closed collapse-closed'


class EventAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields': ('title', 'description', 'venue')
		}),
		('Times', {
			'fields': ('start_date', 'start_time', 'end_date', 'end_time')
		}),
		('Advanced', {
			'fields': ('parent_event', 'uid')
		})
	)
	inlines = [EventInline, EventNoteInline]


class EventNoteAdmin(admin.ModelAdmin):
	list_filter = ('note_type',)
	date_hierarchy = 'timestamp'
	list_display = ('__unicode__', 'event', 'user', 'timestamp', 'note_type')


admin.site.register(Building, BuildingAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventNote, EventNoteAdmin)


class ManageEventsSection(FormAdminSection):
	# I want to have creation on same page as instance list (of user's only.)
	# editing is subsection, but not in nav. Ugh. Pagination. Can wait for now.
	form = EditEventForm
	slug = 'event'
	verbose_name = 'Manage your events'
	order = 40
	changelist_template = 'stepping_out/admin/sections/events.html'
	
	def has_permission(self, request):
		opts = Event._meta
		return request.user.is_authenticated() and request.user.is_active and \
			request.user.has_perm('%s.%s' % (opts.app_label, opts.get_add_permission())) \
			and request.user.has_perm('%s.%s' % (opts.app_label, opts.get_change_permission()))
	
	@property
	def urls(self):
		def wrap(view, cacheable=False):
			return self.admin_view(view, cacheable)
		
		urlpatterns = patterns('',
			url(r'^$', wrap(self.basic_view),
				name='%s_%s' % (self.admin_site.url_prefix, self.slug)),
			url(r'^edit/(?P<event_id>\d+)/$', wrap(self.edit_view),
				name='%s_%s_edit' % (self.admin_site.url_prefix, self.slug))
		)
		return urlpatterns
	
	def basic_view(self, request, extra_context=None):
		if request.method == 'POST':
			form = self.form(request.user, request.POST, request.FILES)
			
			if form.is_valid():
				form.save()
				return HttpResponseRedirect('')
		else:
			form = self.form(request.user)
		
		extra_context = extra_context or {}
		extra_context.update({
			'form': form,
			'events': Event.objects.filter(owner=request.user)
		})
		return super(FormAdminSection, self).basic_view(request, template=self.changelist_template, extra_context=extra_context)
	
	def edit_view(self, request, event_id, extra_context=None):
		instance = get_object_or_404(Event, pk=event_id, owner=request.user)
		
		if request.method == 'POST':
			form = self.form(request.user, request.POST, request.FILES, instance=instance)
			
			if form.is_valid():
				form.save()
				return HttpResponseRedirect('')
		else:
			form = self.form(request.user, instance=instance)
		
		extra_context = extra_context or {}
		extra_context.update({
			'form': form,
		})
		return super(FormAdminSection, self).basic_view(request, extra_context=extra_context)


site.register(ManageEventsSection)
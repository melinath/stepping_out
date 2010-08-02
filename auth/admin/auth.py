from stepping_out.auth.models.auth import *
from django.contrib import admin
from django import forms


class OfficerPositionInline(admin.TabularInline):
	model = OfficerUserMetaInfo
	filter_horizontal = ('terms',)
	verbose_name = 'officer position'
	verbose_name_plural = 'officer positions'
	extra = 1
	classes = ('collapse', 'collapse-closed', 'closed',)


class OfficerPositionAdmin(admin.ModelAdmin):
	list_editable = ['order']
	list_display = ['name', 'order'] 


class TermAdminForm(forms.ModelForm):
	class Meta:
		model = Term
	
	def clean_end(self):
		if(self.cleaned_data['end']<self.cleaned_data['start']):
			raise forms.ValidationError('A term cannot end before it starts!')
			
		return self.cleaned_data['end']


class TermAdmin(admin.ModelAdmin):
	list_display = ['name', 'start', 'end']
	form = TermAdminForm


class PendConfirmationDataInline(admin.TabularInline):
	model = PendConfirmationData


class PendConfirmationAdmin(admin.ModelAdmin):
	inlines = [PendConfirmationDataInline]


admin.site.register(OfficerPosition, OfficerPositionAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(PendConfirmation, PendConfirmationAdmin)
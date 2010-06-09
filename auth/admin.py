from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from models import UserProfile, OfficerPosition, UserEmail, Term, OfficerUserMetaInfo, OfficerPosition
from django.db.models import CharField
from settings import IMPORTED_USER_INLINES, IMPORTED_GROUP_INLINES
from django import forms

class UserProfileInline(admin.TabularInline):
    model = UserProfile
    
class UserEmailInline(admin.TabularInline):
    model = UserEmail

class OfficerPositionInline(admin.StackedInline):
    model = OfficerUserMetaInfo
    filter_horizontal = ['terms']
    
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

USER_INLINES = [
    UserEmailInline,
    UserProfileInline,
    OfficerPositionInline,
]
USER_INLINES += IMPORTED_USER_INLINES

GROUP_INLINES = [
]
GROUP_INLINES += IMPORTED_GROUP_INLINES

class MyUserAdmin(UserAdmin):
    inlines = USER_INLINES
    """
    formfield_overrides = {
        CharField: {'required' : True}
    }
    """
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (('Groups'), {'fields': ('groups',)}),
    )
    filter_horizontal = ('groups',)
    
class MyGroupAdmin(GroupAdmin):
    inlines = GROUP_INLINES

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, MyUserAdmin)
admin.site.register(Group, MyGroupAdmin)
admin.site.register(OfficerPosition, OfficerPositionAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(OfficerUserMetaInfo)
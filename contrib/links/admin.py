from models import LinkMetaInfo, Link, Category
from django.contrib import admin
from django import forms

class LinkMetaInfoInline(admin.TabularInline):
    model = LinkMetaInfo
    extra = 1
    raw_id_fields = ('category', 'link',)
    
class LinkAdmin(admin.ModelAdmin):
    inlines = [
        LinkMetaInfoInline,
    ]
    fields = ('name', 'url')
    list_display = ('name', 'url')

"""
class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
    
    def clean_parent(self):
        parent = self.cleaned_data['parent']
        
        self.check_parentage()
        
        return parent
"""

class CategoryAdmin(admin.ModelAdmin):
    #form = CategoryAdminForm
    raw_id_fields=('parent',)
    list_display = ('name', 'parent_name', 'path',)
    #ordering = ('parent',)
    search_fields = ['name',]

admin.site.register(Link, LinkAdmin)
admin.site.register(Category, CategoryAdmin)
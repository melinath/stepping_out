from django.contrib import admin
from django.contrib.contenttypes import generic
from stepping_out.pricing.models import PricePackage, PriceClass


# This is only useful in the bright future where nested inlines roam free.
#class PricePackageInline(generic.GenericTabularInline):
#	model = PricePackage
#	ct_field = 'attached_content_type'
#	ct_fk_field = 'attached_object_id'


class PriceClassInline(admin.TabularInline):
	model = PriceClass
	verbose_name_plural = 'price classes'


class PricePackageAdmin(admin.ModelAdmin):
	inlines=[
		PriceClassInline
	]


admin.site.register(PricePackage, PricePackageAdmin)
from django.contrib import admin
from django.contrib.contenttypes import generic
from stepping_out.pricing.models import PricePackage, PriceClass, Price


# This is only useful in the bright future where nested inlines roam free.
#class PricePackageInline(generic.GenericTabularInline):
#	model = PricePackage
#	ct_field = 'attached_content_type'
#	ct_fk_field = 'attached_object_id'


class PriceClassInline(admin.TabularInline):
	model = PriceClass


class PricePackageAdmin(admin.ModelAdmin):
	inlines=[
		PriceClassInline
	]


class PriceInline(admin.TabularInline):
	model = Price
	max_num = 0
	extra = 0
	can_delete = False
	template = 'admin/stepping_out/price/edit_inline/price_inlines.html'


class PriceClassAdmin(admin.ModelAdmin):
	inlines = [
		PriceInline
	]


admin.site.register(PricePackage, PricePackageAdmin)
admin.site.register(PriceClass, PriceClassAdmin)
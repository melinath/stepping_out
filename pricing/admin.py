from django.contrib import admin
from django.contrib.contenttypes import generic
from stepping_out.pricing.models import PricePackage, PriceOption, Price, Payment
from stepping_out.pricing.people import registry


class PricePackageInline(generic.GenericStackedInline):
	model = PricePackage
	ct_field = 'event_content_type'
	ct_fk_field = 'event_object_id'
	extra = 0


class PriceOptionInline(admin.TabularInline):
	model = PriceOption


class PricePackageAdmin(admin.ModelAdmin):
	inlines=[
		PriceOptionInline
	]
	def __init__(self, *args, **kwargs):
		# HACK - iterchoices isn't being cached correctly.
		PricePackage._meta.get_field('person_types')._choices = registry.iterchoices()
		super(PricePackageAdmin, self).__init__(*args, **kwargs)


class PriceInline(admin.TabularInline):
	model = Price
	max_num = 0
	extra = 0
	can_delete = False
	template = 'admin/stepping_out/price/edit_inline/price_inlines.html'


class PriceOptionAdmin(admin.ModelAdmin):
	inlines = [
		PriceInline
	]


class PaymentAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'method', 'paid')


admin.site.register(PricePackage, PricePackageAdmin)
admin.site.register(PriceOption, PriceOptionAdmin)
admin.site.register(Payment, PaymentAdmin)
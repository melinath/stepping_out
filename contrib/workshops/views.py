from stepping_out.contrib.workshops.models import WorkshopUserMetaInfo, Workshop
from stepping_out.pricing.models import Payment
from stepping_out.housing.models import OfferedHousing, RequestedHousing
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.template.defaultfilters import date
from django.http import HttpResponse


registration_row = """
<tr>
	<th>%s</th><!-- name -->
	<td>%s</td><!-- email -->
	<td>%s</td><!-- dancing as... -->
	<td>%s</td><!-- track -->
	<td>%s</td><!-- registration time -->
	<td>%s</td><!-- price -->
	<td>%s</td><!-- paid -->
</tr>"""


def export_registration(request):
	"""Hacked-together view to display workshop data ack!"""
	text = "<table><caption>Total registrants: %s</caption>" % WorkshopUserMetaInfo.objects.count()
	text += registration_row % (
		"Name",
		"Email",
		"Dancing as",
		"Track",
		"Registration Time",
		"Price",
		"Paid"
	)
	ct = ContentType.objects.get_for_model(Workshop)
	for info in WorkshopUserMetaInfo.objects.all():
		paid = Payment.objects.filter(payment_for_id=info.workshop.id, payment_for_ct=ct, user=info.user).aggregate(Sum('paid'))['paid__sum']
		text += registration_row % (
			info.user.get_full_name(),
			info.user.email,
			info.dancing_as == 'l' and 'Lead' or 'Follow',
			info.track,
			date(info.registered_at, "F d Y, H:i:s"),
			info.price.price,
			paid or '0.00'
		)
	text += "</table>"
	return HttpResponse(text)


requested_housing_row = """
<tr>
	<th>%s</th><!-- name -->
	<td>%s</td><!-- email -->
	<td>%s</td><!-- nonsmoking ... -->
	<td>%s</td><!-- no cats -->
	<td>%s</td><!-- no dogs -->
	<td>%s</td><!-- comments -->
</tr>"""


offered_housing_row = """
<tr>
	<th>%s</th><!-- name -->
	<td>%s</td><!-- email -->
	<td>%s</td><!-- address -->
	<td>%s</td><!-- smoking ... -->
	<td>%s</td><!-- cats -->
	<td>%s</td><!-- dogs -->
	<td>%s</td><!-- ideal -->
	<td>%s</td><!-- max -->
	<td>%s</td><!-- comments -->
</tr>"""


def export_housing(request):
	"""Hacked-together view to display workshop data ack!"""
	text = "<table><caption>Total requesters: %s</caption>" % RequestedHousing.objects.count()
	text += requested_housing_row % (
		"Name",
		"Email",
		"Nonsmoking",
		"No cats",
		"No dogs",
		"Comments",
	)
	def translate_choice(val):
		if val == 0:
			return "I don't care"
		elif val == 1:
			return "Preferred"
		return "A must"
	
	for request in RequestedHousing.objects.all():
		text += requested_housing_row % (
			request.user.get_full_name(),
			request.user.email,
			translate_choice(request.nonsmoking),
			translate_choice(request.no_cats),
			translate_choice(request.no_dogs),
			request.comments
		)
	text += "</table><table><caption>Total offerers: %s</caption>" %  OfferedHousing.objects.count()
	text += offered_housing_row % (
		"Name",
		"Email",
		"Address",
		"Smoking",
		"Cats",
		"Dogs",
		"Ideal",
		"Max",
		"Comments",
	)
	
	for offer in OfferedHousing.objects.all():
		text += offered_housing_row % (
			offer.user.get_full_name(),
			offer.user.email,
			offer.address,
			offer.smoking,
			offer.cats,
			offer.dogs,
			offer.num_ideal,
			offer.num_max,
			offer.comments
		)
	text += "</table>"
	return HttpResponse(text)

from stepping_out.contrib.workshops.models import WorkshopUserMetaInfo, Workshop
from stepping_out.pricing.models import Payment
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.template.defaultfilters import date
from django.http import HttpResponse


row = """
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
	text += row % (
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
		text += row % (
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

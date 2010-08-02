from stepping_out.auth.models import PendConfirmation
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext


def confirm_pended_action(request, code, template='stepping_out/registration/pended_action_confirm.html'):
	try:
		pend = PendConfirmation.objects.get(code=code)
	except:
		raise Http404
	else:
		pend.confirm()
	
	context = {
		'pend': pend
	}
	context_instance = RequestContext(request)
	
	return render_to_response(template, context, context_instance=context_instance)
from django import forms
from django.core.exceptions import ValidationError
from stepping_out.mail.models import UserEmail, MailingList


class HoneypotForm(forms.Form):
	honeypot = forms.CharField(help_text="If you enter anything in this field, your subscription will be treated as spam.")
	
	def clean_honeypot(self):
		value = self.cleaned_data['honeypot']
		
		if value:
			raise ValidationError("The honeypot field must be blank!")
		
		return value


class EasySubscriptionForm(forms.ModelForm, HoneypotForm):
	mailing_lists = forms.models.ModelMultipleChoiceField(qs=MailingList.objects.filter(self_subscribe=True))
	
	class Meta:
		model = UserEmail
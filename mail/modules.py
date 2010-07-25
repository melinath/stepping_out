from stepping_out.modules import ModelProxy, Module, ChoiceOfManyField, site, ModuleAdmin
from stepping_out.mail.models import MailingList


class MailingListProxy(ModelProxy):
	model = MailingList
	related_field_name = 'subscribed_users'


class MailingListModule(Module):
	verbose_name = "Mailing list subscriptions"
	slug = 'subscriptions'
	mailing_lists = ChoiceOfManyField(MailingListProxy, required=False)


class MailingListAdmin(ModuleAdmin):
	order = 1


site.register(MailingListModule, MailingListAdmin)
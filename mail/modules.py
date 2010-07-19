from stepping_out.modules import ModuleMultiModel, Module, Section, site
from stepping_out.mail.models import MailingList


class MailingListModel(ModuleMultiModel):
	model = MailingList
	related_field = 'subscribed_users'


class MailingListModule(Module):
	models = (
		MailingListModel(
			field_name='mailing_lists',
			limit_choices_to={'self_subscribe_enabled': True}),
	)


class MailingListSection(Section):
	modules = [
		MailingListModule
	]


site.register(MailingListSection)
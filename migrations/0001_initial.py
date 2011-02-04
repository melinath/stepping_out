# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PricePackage'
        db.create_table('stepping_out_pricepackage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('event_content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('event_object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('available_until', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('person_types', self.gf('stepping_out.pricing.fields.SlugListField')()),
        ))
        db.send_create_signal('stepping_out', ['PricePackage'])

        # Adding model 'PriceOption'
        db.create_table('stepping_out_priceoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(related_name='options', to=orm['stepping_out.PricePackage'])),
        ))
        db.send_create_signal('stepping_out', ['PriceOption'])

        # Adding model 'Price'
        db.create_table('stepping_out_price', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(related_name='prices', to=orm['stepping_out.PriceOption'])),
            ('person_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal('stepping_out', ['Price'])

        # Adding unique constraint on 'Price', fields ['option', 'person_type']
        db.create_unique('stepping_out_price', ['option_id', 'person_type'])

        # Adding model 'Payment'
        db.create_table('stepping_out_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payment_for_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('payment_for_ct', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('paid', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('payment_method', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('payment_made', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('ipn', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ipn.PayPalIPN'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('stepping_out', ['Payment'])

        # Adding model 'OfferedHousing'
        db.create_table('stepping_out_offeredhousing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('coordinator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='offered_housing', to=orm['stepping_out.HousingCoordinator'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('smoking', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cats', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dogs', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('num_ideal', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('num_max', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('stepping_out', ['OfferedHousing'])

        # Adding unique constraint on 'OfferedHousing', fields ['coordinator', 'user']
        db.create_unique('stepping_out_offeredhousing', ['coordinator_id', 'user_id'])

        # Adding model 'RequestedHousing'
        db.create_table('stepping_out_requestedhousing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('coordinator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requested_housing', to=orm['stepping_out.HousingCoordinator'])),
            ('nonsmoking', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('no_cats', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('no_dogs', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('housed_with', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='housed', null=True, to=orm['stepping_out.OfferedHousing'])),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('stepping_out', ['RequestedHousing'])

        # Adding model 'HousingCoordinator'
        db.create_table('stepping_out_housingcoordinator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event_content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('event_object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('stepping_out', ['HousingCoordinator'])

        # Adding unique constraint on 'HousingCoordinator', fields ['event_content_type', 'event_object_id']
        db.create_unique('stepping_out_housingcoordinator', ['event_content_type_id', 'event_object_id'])

        # Adding model 'Term'
        db.create_table('stepping_out_term', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
        ))
        db.send_create_signal('stepping_out', ['Term'])

        # Adding model 'OfficerUserMetaInfo'
        db.create_table('stepping_out_officerusermetainfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('officer_position', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stepping_out.OfficerPosition'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('stepping_out', ['OfficerUserMetaInfo'])

        # Adding M2M table for field terms on 'OfficerUserMetaInfo'
        db.create_table('stepping_out_officerusermetainfo_terms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('officerusermetainfo', models.ForeignKey(orm['stepping_out.officerusermetainfo'], null=False)),
            ('term', models.ForeignKey(orm['stepping_out.term'], null=False))
        ))
        db.create_unique('stepping_out_officerusermetainfo_terms', ['officerusermetainfo_id', 'term_id'])

        # Adding model 'OfficerPosition'
        db.create_table('stepping_out_officerposition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('stepping_out', ['OfficerPosition'])

        # Adding M2M table for field permissions on 'OfficerPosition'
        db.create_table('stepping_out_officerposition_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('officerposition', models.ForeignKey(orm['stepping_out.officerposition'], null=False)),
            ('permission', models.ForeignKey(orm['auth.permission'], null=False))
        ))
        db.create_unique('stepping_out_officerposition_permissions', ['officerposition_id', 'permission_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'HousingCoordinator', fields ['event_content_type', 'event_object_id']
        db.delete_unique('stepping_out_housingcoordinator', ['event_content_type_id', 'event_object_id'])

        # Removing unique constraint on 'OfferedHousing', fields ['coordinator', 'user']
        db.delete_unique('stepping_out_offeredhousing', ['coordinator_id', 'user_id'])

        # Removing unique constraint on 'Price', fields ['option', 'person_type']
        db.delete_unique('stepping_out_price', ['option_id', 'person_type'])

        # Deleting model 'PricePackage'
        db.delete_table('stepping_out_pricepackage')

        # Deleting model 'PriceOption'
        db.delete_table('stepping_out_priceoption')

        # Deleting model 'Price'
        db.delete_table('stepping_out_price')

        # Deleting model 'Payment'
        db.delete_table('stepping_out_payment')

        # Deleting model 'OfferedHousing'
        db.delete_table('stepping_out_offeredhousing')

        # Deleting model 'RequestedHousing'
        db.delete_table('stepping_out_requestedhousing')

        # Deleting model 'HousingCoordinator'
        db.delete_table('stepping_out_housingcoordinator')

        # Deleting model 'Term'
        db.delete_table('stepping_out_term')

        # Deleting model 'OfficerUserMetaInfo'
        db.delete_table('stepping_out_officerusermetainfo')

        # Removing M2M table for field terms on 'OfficerUserMetaInfo'
        db.delete_table('stepping_out_officerusermetainfo_terms')

        # Deleting model 'OfficerPosition'
        db.delete_table('stepping_out_officerposition')

        # Removing M2M table for field permissions on 'OfficerPosition'
        db.delete_table('stepping_out_officerposition_permissions')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ipn.paypalipn': {
            'Meta': {'object_name': 'PayPalIPN', 'db_table': "'paypal_ipn'"},
            'address_city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'address_country': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'address_country_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'address_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'address_state': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'address_status': ('django.db.models.fields.CharField', [], {'max_length': '11', 'blank': 'True'}),
            'address_street': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'address_zip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'amount1': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'amount2': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'amount3': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'amount_per_cycle': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'auction_buyer_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'auction_closing_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'auction_multi_item': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'auth_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'auth_exp': ('django.db.models.fields.CharField', [], {'max_length': '28', 'blank': 'True'}),
            'auth_id': ('django.db.models.fields.CharField', [], {'max_length': '19', 'blank': 'True'}),
            'auth_status': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'business': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'case_creation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'case_id': ('django.db.models.fields.CharField', [], {'max_length': '14', 'blank': 'True'}),
            'case_type': ('django.db.models.fields.CharField', [], {'max_length': '24', 'blank': 'True'}),
            'charset': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency_code': ('django.db.models.fields.CharField', [], {'default': "'USD'", 'max_length': '32', 'blank': 'True'}),
            'custom': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'exchange_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '16', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'flag_code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'flag_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'for_auction': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'from_view': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'handling_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_payment_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'invoice': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'ipaddress': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'blank': 'True'}),
            'item_name': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'item_number': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'mc_amount1': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'mc_amount2': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'mc_amount3': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'mc_currency': ('django.db.models.fields.CharField', [], {'default': "'USD'", 'max_length': '32', 'blank': 'True'}),
            'mc_fee': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'mc_gross': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'mc_handling': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'mc_shipping': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'memo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'next_payment_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'notify_version': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'num_cart_items': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'option_name1': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'option_name2': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'outstanding_balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'parent_txn_id': ('django.db.models.fields.CharField', [], {'max_length': '19', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '24', 'blank': 'True'}),
            'payer_business_name': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'payer_email': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'payer_id': ('django.db.models.fields.CharField', [], {'max_length': '13', 'blank': 'True'}),
            'payer_status': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'payment_cycle': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'payment_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'payment_gross': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'payment_status': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'payment_type': ('django.db.models.fields.CharField', [], {'max_length': '7', 'blank': 'True'}),
            'pending_reason': ('django.db.models.fields.CharField', [], {'max_length': '14', 'blank': 'True'}),
            'period1': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'period2': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'period3': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'period_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'product_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'product_type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'profile_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'protection_eligibility': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reason_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'reattempt': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'receipt_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'receiver_email': ('django.db.models.fields.EmailField', [], {'max_length': '127', 'blank': 'True'}),
            'receiver_id': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'recur_times': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'recurring': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'recurring_payment_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'remaining_settle': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'residence_country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'retry_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rp_invoice_id': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'settle_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'settle_currency': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'shipping_method': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'subscr_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subscr_effective': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subscr_id': ('django.db.models.fields.CharField', [], {'max_length': '19', 'blank': 'True'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'test_ipn': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'transaction_entity': ('django.db.models.fields.CharField', [], {'max_length': '7', 'blank': 'True'}),
            'transaction_subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'txn_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '19', 'blank': 'True'}),
            'txn_type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'verify_sign': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'stepping_out.housingcoordinator': {
            'Meta': {'unique_together': "(('event_content_type', 'event_object_id'),)", 'object_name': 'HousingCoordinator'},
            'event_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'event_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offering_users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'housing_coordinator_offered_set'", 'symmetrical': 'False', 'through': "orm['stepping_out.OfferedHousing']", 'to': "orm['auth.User']"}),
            'requesting_users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'housing_coordinator_requested_set'", 'symmetrical': 'False', 'through': "orm['stepping_out.RequestedHousing']", 'to': "orm['auth.User']"})
        },
        'stepping_out.offeredhousing': {
            'Meta': {'unique_together': "(['coordinator', 'user'],)", 'object_name': 'OfferedHousing'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'cats': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offered_housing'", 'to': "orm['stepping_out.HousingCoordinator']"}),
            'dogs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_ideal': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'num_max': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'smoking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'stepping_out.officerposition': {
            'Meta': {'object_name': 'OfficerPosition'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Permission']", 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['stepping_out.OfficerUserMetaInfo']", 'symmetrical': 'False'})
        },
        'stepping_out.officerusermetainfo': {
            'Meta': {'object_name': 'OfficerUserMetaInfo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'officer_position': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stepping_out.OfficerPosition']"}),
            'terms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['stepping_out.Term']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'stepping_out.payment': {
            'Meta': {'object_name': 'Payment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ipn.PayPalIPN']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'payment_for_ct': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'payment_for_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'payment_made': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'stepping_out.price': {
            'Meta': {'unique_together': "(['option', 'person_type'],)", 'object_name': 'Price'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': "orm['stepping_out.PriceOption']"}),
            'person_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'})
        },
        'stepping_out.priceoption': {
            'Meta': {'object_name': 'PriceOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'options'", 'to': "orm['stepping_out.PricePackage']"})
        },
        'stepping_out.pricepackage': {
            'Meta': {'ordering': "['available_until']", 'object_name': 'PricePackage'},
            'available_until': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'event_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'event_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'person_types': ('stepping_out.pricing.fields.SlugListField', [], {})
        },
        'stepping_out.requestedhousing': {
            'Meta': {'object_name': 'RequestedHousing'},
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requested_housing'", 'to': "orm['stepping_out.HousingCoordinator']"}),
            'housed_with': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'housed'", 'null': 'True', 'to': "orm['stepping_out.OfferedHousing']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'no_cats': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'no_dogs': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'nonsmoking': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'stepping_out.term': {
            'Meta': {'object_name': 'Term'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['stepping_out']

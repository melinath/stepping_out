# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'OfferedHousing', fields ['coordinator', 'user'] - except not really since we're deleting the model anyway.
        #db.delete_unique('stepping_out_offeredhousing', ['coordinator_id', 'user_id'])

        # Removing unique constraint on 'HousingCoordinator', fields ['event_content_type', 'event_object_id'] -- don't do this 'cause it's being deleted anyway.
        #db.delete_unique('stepping_out_housingcoordinator', ['event_content_type_id', 'event_object_id'])

        # Deleting model 'HousingCoordinator'
        db.delete_table('stepping_out_housingcoordinator')

        # Deleting model 'RequestedHousing'
        db.delete_table('stepping_out_requestedhousing')

        # Deleting model 'OfferedHousing'
        db.delete_table('stepping_out_offeredhousing')


    def backwards(self, orm):
        
        # Adding model 'HousingCoordinator'
        db.create_table('stepping_out_housingcoordinator', (
            ('event_content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('event_object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('stepping_out', ['HousingCoordinator'])

        # Adding unique constraint on 'HousingCoordinator', fields ['event_content_type', 'event_object_id']
        db.create_unique('stepping_out_housingcoordinator', ['event_content_type_id', 'event_object_id'])

        # Adding model 'RequestedHousing'
        db.create_table('stepping_out_requestedhousing', (
            ('housed_with', self.gf('django.db.models.fields.related.ForeignKey')(related_name='housed', null=True, to=orm['stepping_out.OfferedHousing'], blank=True)),
            ('coordinator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requested_housing', to=orm['stepping_out.HousingCoordinator'])),
            ('no_dogs', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('no_cats', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('nonsmoking', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('stepping_out', ['RequestedHousing'])

        # Adding model 'OfferedHousing'
        db.create_table('stepping_out_offeredhousing', (
            ('coordinator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='offered_housing', to=orm['stepping_out.HousingCoordinator'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('smoking', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('num_ideal', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cats', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('num_max', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('dogs', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('stepping_out', ['OfferedHousing'])

        # Adding unique constraint on 'OfferedHousing', fields ['coordinator', 'user']
        db.create_unique('stepping_out_offeredhousing', ['coordinator_id', 'user_id'])


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
        'stepping_out.officer': {
            'Meta': {'unique_together': "(('user', 'position', 'term'),)", 'object_name': 'Officer'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'officers'", 'to': "orm['stepping_out.OfficerPosition']"}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'officers'", 'to': "orm['stepping_out.Term']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'officers'", 'to': "orm['auth.User']"})
        },
        'stepping_out.officerposition': {
            'Meta': {'object_name': 'OfficerPosition'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Permission']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'officer_positions'", 'symmetrical': 'False', 'through': "orm['stepping_out.Officer']", 'to': "orm['auth.User']"})
        },
        'stepping_out.payment': {
            'Meta': {'object_name': 'Payment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'person_types': ('stepping_out.pricing.fields.SlugMultipleChoiceField', [], {})
        },
        'stepping_out.term': {
            'Meta': {'object_name': 'Term'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'positions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'terms'", 'symmetrical': 'False', 'through': "orm['stepping_out.Officer']", 'to': "orm['stepping_out.OfficerPosition']"}),
            'start': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['stepping_out']

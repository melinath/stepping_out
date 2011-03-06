# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Payment.payment_for_ct'
        db.delete_column('stepping_out_payment', 'payment_for_ct_id')

        # Deleting field 'Payment.user'
        db.delete_column('stepping_out_payment', 'user_id')

        # Deleting field 'Payment.payment_made'
        db.delete_column('stepping_out_payment', 'payment_made')

        # Deleting field 'Payment.payment_method'
        db.delete_column('stepping_out_payment', 'payment_method')

        # Deleting field 'Payment.payment_for_id'
        db.delete_column('stepping_out_payment', 'payment_for_id')

        # Adding field 'Payment.registration'
        db.add_column('stepping_out_payment', 'registration', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='payments', to=orm['workshops.Registration']), keep_default=False)

        # Adding field 'Payment.method'
        db.add_column('stepping_out_payment', 'method', self.gf('django.db.models.fields.CharField')(default='cash', max_length=10), keep_default=False)

        # Adding field 'Payment.timestamp'
        db.add_column('stepping_out_payment', 'timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now), keep_default=False)


    def backwards(self, orm):
        
        # We cannot add back in field 'Payment.payment_for_ct'
        raise RuntimeError(
            "Cannot reverse this migration. 'Payment.payment_for_ct' and its values cannot be restored.")

        # We cannot add back in field 'Payment.user'
        raise RuntimeError(
            "Cannot reverse this migration. 'Payment.user' and its values cannot be restored.")

        # Adding field 'Payment.payment_made'
        db.add_column('stepping_out_payment', 'payment_made', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now), keep_default=False)

        # We cannot add back in field 'Payment.payment_method'
        raise RuntimeError(
            "Cannot reverse this migration. 'Payment.payment_method' and its values cannot be restored.")

        # We cannot add back in field 'Payment.payment_for_id'
        raise RuntimeError(
            "Cannot reverse this migration. 'Payment.payment_for_id' and its values cannot be restored.")

        # Deleting field 'Payment.registration'
        db.delete_column('stepping_out_payment', 'registration_id')

        # Deleting field 'Payment.method'
        db.delete_column('stepping_out_payment', 'method')

        # Deleting field 'Payment.timestamp'
        db.delete_column('stepping_out_payment', 'timestamp')


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
            'method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'registration': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': "orm['workshops.Registration']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
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
        },
        'workshops.registration': {
            'Meta': {'unique_together': "(('workshop', 'user'), ('workshop', 'key'))", 'object_name': 'Registration'},
            'dancing_as': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'price': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stepping_out.Price']"}),
            'registered_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workshops.WorkshopTrack']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'workshop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workshops.Workshop']"})
        },
        'workshops.workshop': {
            'Meta': {'object_name': 'Workshop'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'online_registration_end': ('django.db.models.fields.DateField', [], {}),
            'registered_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['workshops.Registration']", 'symmetrical': 'False'}),
            'registration_start': ('django.db.models.fields.DateField', [], {}),
            'tagline': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'workshop_end': ('django.db.models.fields.DateField', [], {}),
            'workshop_start': ('django.db.models.fields.DateField', [], {})
        },
        'workshops.workshoptrack': {
            'Meta': {'unique_together': "(('workshop', 'name'),)", 'object_name': 'WorkshopTrack'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'workshop': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tracks'", 'to': "orm['workshops.Workshop']"})
        }
    }

    complete_apps = ['stepping_out']

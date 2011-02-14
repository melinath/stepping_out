# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Registration.key'
        db.add_column('workshops_registration', 'key', self.gf('django.db.models.fields.CharField')(default='AAAAAA', max_length=6), keep_default=False)

        # Adding unique constraint on 'WorkshopTrack', fields ['workshop', 'name']
        db.create_unique('workshops_workshoptrack', ['workshop_id', 'name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'WorkshopTrack', fields ['workshop', 'name']
        db.delete_unique('workshops_workshoptrack', ['workshop_id', 'name'])

        # Deleting field 'Registration.key'
        db.delete_column('workshops_registration', 'key')


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
        'workshops.registration': {
            'Meta': {'unique_together': "(('workshop', 'user'),)", 'object_name': 'Registration'},
            'dancing_as': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'price': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stepping_out.Price']"}),
            'registered_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workshops.WorkshopTrack']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
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
        'workshops.workshopevent': {
            'Meta': {'object_name': 'WorkshopEvent'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workshops.WorkshopTrack']", 'null': 'True', 'blank': 'True'}),
            'workshop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workshops.Workshop']"})
        },
        'workshops.workshoptrack': {
            'Meta': {'unique_together': "(('workshop', 'name'),)", 'object_name': 'WorkshopTrack'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'workshop': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tracks'", 'to': "orm['workshops.Workshop']"})
        }
    }

    complete_apps = ['workshops']

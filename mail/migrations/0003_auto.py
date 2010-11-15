# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field moderator_emails on 'MailingList'
        db.create_table('mail_mailinglist_moderator_emails', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm['mail.mailinglist'], null=False)),
            ('useremail', models.ForeignKey(orm['mail.useremail'], null=False))
        ))
        db.create_unique('mail_mailinglist_moderator_emails', ['mailinglist_id', 'useremail_id'])


    def backwards(self, orm):
        
        # Removing M2M table for field moderator_emails on 'MailingList'
        db.delete_table('mail_mailinglist_moderator_emails')


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
        'mail.mailinglist': {
            'Meta': {'unique_together': "(('site', 'address'),)", 'object_name': 'MailingList'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderator_emails': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'moderated_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['mail.UserEmail']"}),
            'moderator_groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'moderated_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'moderator_officer_positions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'moderated_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['stepping_out.OfficerPosition']"}),
            'moderator_users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'moderated_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'self_subscribe_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['sites.Site']"}),
            'subscribed_emails': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subscribed_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['mail.UserEmail']"}),
            'subscribed_groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subscribed_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'subscribed_officer_positions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subscribed_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['stepping_out.OfficerPosition']"}),
            'subscribed_users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subscribed_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'who_can_post': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        'mail.useremail': {
            'Meta': {'object_name': 'UserEmail'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'emails'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        'stepping_out.term': {
            'Meta': {'object_name': 'Term'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['mail']

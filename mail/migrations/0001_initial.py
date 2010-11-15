# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UserEmail'
        db.create_table('mail_useremail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='emails', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('mail', ['UserEmail'])

        # Adding model 'UserList'
        db.create_table('mail_userlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('plugin', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('json_value', self.gf('django.db.models.fields.TextField')(max_length=30, blank=True)),
        ))
        db.send_create_signal('mail', ['UserList'])

        # Adding model 'MailingList'
        db.create_table('mail_mailinglist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['sites.Site'])),
            ('help_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('who_can_post', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('self_subscribe_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('mail', ['MailingList'])

        # Adding unique constraint on 'MailingList', fields ['site', 'address']
        db.create_unique('mail_mailinglist', ['site_id', 'address'])

        # Adding M2M table for field subscribed_users on 'MailingList'
        db.create_table('mail_mailinglist_subscribed_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm['mail.mailinglist'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('mail_mailinglist_subscribed_users', ['mailinglist_id', 'user_id'])

        # Adding M2M table for field subscribed_groups on 'MailingList'
        db.create_table('mail_mailinglist_subscribed_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm['mail.mailinglist'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('mail_mailinglist_subscribed_groups', ['mailinglist_id', 'group_id'])

        # Adding M2M table for field subscribed_userlists on 'MailingList'
        db.create_table('mail_mailinglist_subscribed_userlists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm['mail.mailinglist'], null=False)),
            ('userlist', models.ForeignKey(orm['mail.userlist'], null=False))
        ))
        db.create_unique('mail_mailinglist_subscribed_userlists', ['mailinglist_id', 'userlist_id'])

        # Adding M2M table for field subscribed_emails on 'MailingList'
        db.create_table('mail_mailinglist_subscribed_emails', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm['mail.mailinglist'], null=False)),
            ('useremail', models.ForeignKey(orm['mail.useremail'], null=False))
        ))
        db.create_unique('mail_mailinglist_subscribed_emails', ['mailinglist_id', 'useremail_id'])

        # Adding M2M table for field moderator_users on 'MailingList'
        db.create_table('mail_mailinglist_moderator_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm['mail.mailinglist'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('mail_mailinglist_moderator_users', ['mailinglist_id', 'user_id'])

        # Adding M2M table for field moderator_groups on 'MailingList'
        db.create_table('mail_mailinglist_moderator_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm['mail.mailinglist'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('mail_mailinglist_moderator_groups', ['mailinglist_id', 'group_id'])

        # Adding M2M table for field moderator_userlists on 'MailingList'
        db.create_table('mail_mailinglist_moderator_userlists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm['mail.mailinglist'], null=False)),
            ('userlist', models.ForeignKey(orm['mail.userlist'], null=False))
        ))
        db.create_unique('mail_mailinglist_moderator_userlists', ['mailinglist_id', 'userlist_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'MailingList', fields ['site', 'address']
        db.delete_unique('mail_mailinglist', ['site_id', 'address'])

        # Deleting model 'UserEmail'
        db.delete_table('mail_useremail')

        # Deleting model 'UserList'
        db.delete_table('mail_userlist')

        # Deleting model 'MailingList'
        db.delete_table('mail_mailinglist')

        # Removing M2M table for field subscribed_users on 'MailingList'
        db.delete_table('mail_mailinglist_subscribed_users')

        # Removing M2M table for field subscribed_groups on 'MailingList'
        db.delete_table('mail_mailinglist_subscribed_groups')

        # Removing M2M table for field subscribed_userlists on 'MailingList'
        db.delete_table('mail_mailinglist_subscribed_userlists')

        # Removing M2M table for field subscribed_emails on 'MailingList'
        db.delete_table('mail_mailinglist_subscribed_emails')

        # Removing M2M table for field moderator_users on 'MailingList'
        db.delete_table('mail_mailinglist_moderator_users')

        # Removing M2M table for field moderator_groups on 'MailingList'
        db.delete_table('mail_mailinglist_moderator_groups')

        # Removing M2M table for field moderator_userlists on 'MailingList'
        db.delete_table('mail_mailinglist_moderator_userlists')


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
            'moderator_groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'moderated_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'moderator_userlists': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'moderated_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['mail.UserList']"}),
            'moderator_users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'moderated_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'self_subscribe_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['sites.Site']"}),
            'subscribed_emails': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subscribed_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['mail.UserEmail']"}),
            'subscribed_groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subscribed_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'subscribed_userlists': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subscribed_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['mail.UserList']"}),
            'subscribed_users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subscribed_mailinglist_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'who_can_post': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        'mail.useremail': {
            'Meta': {'object_name': 'UserEmail'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'emails'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'mail.userlist': {
            'Meta': {'object_name': 'UserList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json_value': ('django.db.models.fields.TextField', [], {'max_length': '30', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plugin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['mail']

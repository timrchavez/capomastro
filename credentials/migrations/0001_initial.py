# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SshKeyPair'
        db.create_table(u'credentials_sshkeypair', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('public_key', self.gf('django.db.models.fields.TextField')()),
            ('private_key', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'credentials', ['SshKeyPair'])


    def backwards(self, orm):
        # Deleting model 'SshKeyPair'
        db.delete_table(u'credentials_sshkeypair')


    models = {
        u'credentials.sshkeypair': {
            'Meta': {'object_name': 'SshKeyPair'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'private_key': ('django.db.models.fields.TextField', [], {}),
            'public_key': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['credentials']
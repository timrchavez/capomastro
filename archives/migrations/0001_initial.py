# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Archive'
        db.create_table(u'archives_archive', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('policy', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('basedir', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('ssh_credentials', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credentials.SshKeyPair'])),
            ('transport', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'archives', ['Archive'])


    def backwards(self, orm):
        # Deleting model 'Archive'
        db.delete_table(u'archives_archive')


    models = {
        u'archives.archive': {
            'Meta': {'object_name': 'Archive'},
            'basedir': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'policy': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'ssh_credentials': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['credentials.SshKeyPair']"}),
            'transport': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'credentials.sshkeypair': {
            'Meta': {'object_name': 'SshKeyPair'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'private_key': ('django.db.models.fields.TextField', [], {}),
            'public_key': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['archives']
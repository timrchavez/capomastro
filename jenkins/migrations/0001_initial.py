# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'JenkinsServer'
        db.create_table(u'jenkins_jenkinsserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('remote_addr', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'jenkins', ['JenkinsServer'])

        # Adding model 'JobType'
        db.create_table(u'jenkins_jobtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('config_xml', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'jenkins', ['JobType'])

        # Adding model 'Job'
        db.create_table(u'jenkins_job', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jenkins.JenkinsServer'])),
            ('jobtype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jenkins.JobType'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'jenkins', ['Job'])

        # Adding unique constraint on 'Job', fields ['server', 'name']
        db.create_unique(u'jenkins_job', ['server_id', 'name'])

        # Adding model 'Build'
        db.create_table(u'jenkins_build', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jenkins.Job'])),
            ('build_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('phase', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('console_log', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'jenkins', ['Build'])

        # Adding model 'Artifact'
        db.create_table(u'jenkins_artifact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('build', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jenkins.Build'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'jenkins', ['Artifact'])


    def backwards(self, orm):
        # Removing unique constraint on 'Job', fields ['server', 'name']
        db.delete_unique(u'jenkins_job', ['server_id', 'name'])

        # Deleting model 'JenkinsServer'
        db.delete_table(u'jenkins_jenkinsserver')

        # Deleting model 'JobType'
        db.delete_table(u'jenkins_jobtype')

        # Deleting model 'Job'
        db.delete_table(u'jenkins_job')

        # Deleting model 'Build'
        db.delete_table(u'jenkins_build')

        # Deleting model 'Artifact'
        db.delete_table(u'jenkins_artifact')


    models = {
        u'jenkins.artifact': {
            'Meta': {'object_name': 'Artifact'},
            'build': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jenkins.Build']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'jenkins.build': {
            'Meta': {'ordering': "['-number']", 'object_name': 'Build'},
            'build_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'console_log': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jenkins.Job']"}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'phase': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'jenkins.jenkinsserver': {
            'Meta': {'object_name': 'JenkinsServer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'remote_addr': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'jenkins.job': {
            'Meta': {'unique_together': "(('server', 'name'),)", 'object_name': 'Job'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jobtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jenkins.JobType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jenkins.JenkinsServer']"})
        },
        u'jenkins.jobtype': {
            'Meta': {'object_name': 'JobType'},
            'config_xml': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['jenkins']
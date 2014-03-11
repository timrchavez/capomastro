# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DependencyType'
        db.create_table(u'projects_dependencytype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('config_xml', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'projects', ['DependencyType'])

        # Adding model 'Dependency'
        db.create_table(u'projects_dependency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('dependency_type', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['projects.DependencyType'], unique=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jenkins.Job'], null=True)),
        ))
        db.send_create_signal(u'projects', ['Dependency'])

        # Adding model 'ProjectDependency'
        db.create_table(u'projects_projectdependency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dependency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Dependency'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('auto_track', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('current_build', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jenkins.Build'], null=True)),
        ))
        db.send_create_signal(u'projects', ['ProjectDependency'])

        # Adding model 'Project'
        db.create_table(u'projects_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'projects', ['Project'])


    def backwards(self, orm):
        # Deleting model 'DependencyType'
        db.delete_table(u'projects_dependencytype')

        # Deleting model 'Dependency'
        db.delete_table(u'projects_dependency')

        # Deleting model 'ProjectDependency'
        db.delete_table(u'projects_projectdependency')

        # Deleting model 'Project'
        db.delete_table(u'projects_project')


    models = {
        u'jenkins.build': {
            'Meta': {'ordering': "['-number']", 'object_name': 'Build'},
            'build_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jenkins.Job']"}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'jenkins.jenkinsserver': {
            'Meta': {'object_name': 'JenkinsServer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'jenkins.job': {
            'Meta': {'object_name': 'Job'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'server': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['jenkins.JenkinsServer']", 'unique': 'True'})
        },
        u'projects.dependency': {
            'Meta': {'object_name': 'Dependency'},
            'dependency_type': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['projects.DependencyType']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jenkins.Job']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'projects.dependencytype': {
            'Meta': {'object_name': 'DependencyType'},
            'config_xml': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'projects.project': {
            'Meta': {'object_name': 'Project'},
            'dependencies': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['projects.Dependency']", 'through': u"orm['projects.ProjectDependency']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'projects.projectdependency': {
            'Meta': {'object_name': 'ProjectDependency'},
            'auto_track': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'current_build': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jenkins.Build']", 'null': 'True'}),
            'dependency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Dependency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"})
        }
    }

    complete_apps = ['projects']
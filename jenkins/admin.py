from django.contrib import admin

from jenkins.models import JenkinsServer, Job, Build, Artifact

admin.site.register(JenkinsServer)
admin.site.register(Job)
admin.site.register(Build)
admin.site.register(Artifact)

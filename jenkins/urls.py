from django.conf.urls import patterns, url, include

from jenkins.views import *

# TODO Standardise names on either plural_ or singular_
urlpatterns = patterns("",
    url(r"^notifications/$", NotificationHandlerView.as_view(), name="jenkins_notifications"),
    url(r"^servers/$", JenkinsServerListView.as_view(), name="jenkinsserver_index"),
    url(r"^servers/(?P<pk>\d+)/$", JenkinsServerDetailView.as_view(), name="jenkinsserver_detail"),
    url(r"^servers/(?P<server_pk>\d+)/jobs/(?P<job_pk>\d+)/",
      JenkinsServerJobBuildsIndexView.as_view(), name="jenkinsserver_job_builds_index"),
)

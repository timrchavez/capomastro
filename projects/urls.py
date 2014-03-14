from django.conf.urls import patterns, url, include

from projects.views import *


urlpatterns = patterns("",
    url(r"^projects/$", ProjectListView.as_view(), name="project_list"),
    url(r"^projects/(?P<pk>\d+)/$", ProjectDetailView.as_view(), name="project_detail"),
    url(r"^projects/(?P<pk>\d+)/build/$", InitiateProjectBuildView.as_view(), name="project_initiate_projectbuild"),
    url(r"^projects/(?P<pk>\d+)/builds/$", ProjectBuildListView.as_view(), name="project_projectbuild_list"),
    url(r"^projects/(?P<project_pk>\d+)/builds/(?P<build_pk>\d+)$", ProjectBuildDetailView.as_view(), name="project_projectbuild_detail"),
    url(r"^projects/create/$", ProjectCreateView.as_view(), name="project_create"),
    url(r"^dependencies/create/$", DependencyCreateView.as_view(), name="dependency_create"),
    url(r"^dependencies/$", DependencyListView.as_view(), name="dependency_list"),
    url(r"^dependencies/(?P<pk>\d+)/$", DependencyDetailView.as_view(), name="dependency_detail"),
)

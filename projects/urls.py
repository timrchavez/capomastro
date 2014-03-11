from django.conf.urls import patterns, url, include

from projects.views import *


urlpatterns = patterns("",
    url(r"^projects/$", ProjectListView.as_view(), name="projects_index"),
    url(r"^projects/(?P<pk>\d+)/$", ProjectDetailView.as_view(), name="projects_detail"),
    url(r"^projects/create/$", ProjectCreateView.as_view(), name="projects_create"),
    url(r"^dependencies/create/$", DependencyCreateView.as_view(), name="dependency_create"),
)

from django.conf.urls import patterns, include, url
from django.contrib import admin

from wooster.views import HomeView


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wooster.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^', include('projects.urls')),
    url(r'^jenkins/', include('jenkins.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

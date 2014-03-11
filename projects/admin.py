from django.contrib import admin

from projects.models import Dependency, DependencyType, Project


admin.site.register(DependencyType)
admin.site.register(Dependency)
admin.site.register(Project)

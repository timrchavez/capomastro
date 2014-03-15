from django.contrib import admin

from projects.models import Dependency, Project


class ProjectDependencyInline(admin.TabularInline):
    model = Project.dependencies.through


class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectDependencyInline]

admin.site.register(Dependency)
admin.site.register(Project, ProjectAdmin)

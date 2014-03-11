from django.shortcuts import get_list_or_404
from django.forms import ModelForm, BooleanField

from projects.models import Project, Dependency, ProjectDependency


class ProjectForm(ModelForm):

    auto_track = BooleanField(
        help_text="Auto track dependencies", required=False)

    class Meta:
        model = Project

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        project.save()
        dependencies = get_list_or_404(
            Dependency, pk__in=self.data["dependencies"])

        for dependency in dependencies:
            project_dependency = ProjectDependency.objects.create(
                project=project, dependency=dependency,
                auto_track=self.data["auto_track"],
                current_build=dependency.get_current_build())
        return project

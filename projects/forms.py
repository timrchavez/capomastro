from django import forms

from jenkins.models import JenkinsServer, JobType
from projects.models import Project, Dependency, ProjectDependency


class ProjectForm(forms.ModelForm):

    auto_track = forms.BooleanField(
        help_text="Auto track dependencies", required=False)

    class Meta:
        model = Project

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        project.save()
        for dependency in self.cleaned_data["dependencies"]:
            project_dependency = ProjectDependency.objects.create(
                project=project, dependency=dependency,
                auto_track=self.data.get("auto_track", False),
                current_build=dependency.get_current_build())
        return project


class DependencyForm(forms.ModelForm):

    jobtype = forms.ModelChoiceField(
        queryset=JobType.objects, required=True)
    server = forms.ModelChoiceField(
        queryset=JenkinsServer.objects, required=True)

    class Meta:
        model = Dependency
        exclude = ["job"]

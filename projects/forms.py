from django import forms

from jenkins.models import JenkinsServer, JobType
from projects.models import (
    Project, Dependency, ProjectDependency, ProjectBuild)
from jenkins.helpers import create_job
from jenkins.tasks import push_job_to_jenkins


class ProjectForm(forms.ModelForm):

    auto_track = forms.BooleanField(
        help_text="Auto track dependencies", required=False)

    class Meta:
        model = Project

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        project.save()

        # TODO: This probably shouldn't use the get_current_build if
        # auto_track=False
        for dependency in self.cleaned_data["dependencies"]:
            ProjectDependency.objects.create(
                project=project, dependency=dependency,
                auto_track=self.data.get("auto_track", False),
                current_build=dependency.get_current_build())
        return project


class DependencyForm(forms.ModelForm):

    jobtype = forms.ModelChoiceField(
        queryset=JobType.objects, required=True, label="Job type",
        help_text="Select a job type to use.")
    server = forms.ModelChoiceField(
        queryset=JenkinsServer.objects, required=True)

    class Meta:
        model = Dependency
        exclude = ["job"]

    def save(self, commit=True):
        dependency = super(DependencyForm, self).save(commit=commit)
        job = create_job(
            self.cleaned_data["jobtype"], self.cleaned_data["server"])
        push_job_to_jenkins.delay(job.pk)
        dependency.job = job
        dependency.save()
        return dependency

class ProjectBuildForm(forms.Form):

    dependencies = forms.ModelMultipleChoiceField(Dependency.objects,
        required=True, widget=forms.CheckboxSelectMultiple)

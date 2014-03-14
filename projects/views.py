from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, View
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from braces.views import (
    LoginRequiredMixin, PermissionRequiredMixin, FormValidMessageMixin,
    SuccessURLRedirectListMixin)

from jenkins.models import Build
from projects.models import (
    Project, Dependency, ProjectDependency, ProjectBuild)
from projects.forms import ProjectForm, DependencyForm
from projects.helpers import build_project


class ProjectCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, FormValidMessageMixin,
    CreateView):

    permission_required = "projects.add_project"
    form_valid_message = "Project created"
    model = Project
    form_class = ProjectForm

    def get_success_url(self):
      return reverse("project_detail", kwargs={"pk": self.object.pk})


class ProjectListView(LoginRequiredMixin, ListView):

    model = Project


class InitiateProjectBuildView(LoginRequiredMixin, View):
    """
    Starts building a project and redirects to the newly created ProjectBuild.
    """

    def post(self, request, pk):
        project = Project.objects.get(pk=pk)
        projectbuild = build_project(project, user=request.user)
        messages.add_message(
            request, messages.INFO, "Build '%s' Queued." % projectbuild.build_id)

        url_args = {"project_pk": project.pk, "build_pk": projectbuild.pk}
        url = reverse("project_projectbuild_detail", kwargs=url_args)
        return HttpResponseRedirect(url)


class ProjectBuildListView(LoginRequiredMixin, ListView):

    context_object_name = "projectbuilds"
    model = ProjectBuild

    def get_queryset(self):
        return ProjectBuild.objects.filter(project=self._get_project_from_url())

    def _get_project_from_url(self):
        return get_object_or_404(Project, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        """
        Supplement the projectbuilds with the project:
        """
        context = super(
            ProjectBuildListView, self).get_context_data(**kwargs)
        context["project"] = self._get_project_from_url()
        return context


class ProjectBuildDetailView(LoginRequiredMixin, DetailView):

    context_object_name = "projectbuild"
    model = ProjectBuild

    def get_object(self):
        return get_object_or_404(ProjectBuild,
            project__pk=self.kwargs["project_pk"], pk=self.kwargs["build_pk"])

    def _get_project_from_url(self):
        return get_object_or_404(Project, pk=self.kwargs["project_pk"])

    def _get_related_builds(self, projectbuild):
        return Build.objects.filter(build_id=projectbuild.build_id)

    def get_context_data(self, **kwargs):
        """
        Supplement the projectbuilds with the project:
        """
        context = super(
            ProjectBuildDetailView, self).get_context_data(**kwargs)
        context["project"] = self._get_project_from_url()
        context["builds"] = self._get_related_builds(context["projectbuild"])
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):

    model = Project
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        """
        Supplement the project with its dependencies.
        """
        context = super(
            ProjectDetailView, self).get_context_data(**kwargs)
        context["dependencies"] = ProjectDependency.objects.filter(
            project=context["project"])
        return context


class DependencyCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, FormValidMessageMixin, CreateView):

    permission_required = "projects.add_dependency"
    form_valid_message = "Dependency created"
    form_class = DependencyForm
    model = Dependency

    def get_success_url(self):
        url_args = {"pk": self.object.pk}
        return reverse("dependency_detail", kwargs=url_args)


class DependencyListView(LoginRequiredMixin, ListView):

    context_object_name = "dependencies"
    model = Dependency


class DependencyDetailView(LoginRequiredMixin, DetailView):

    context_object_name = "dependency"
    model = Dependency


__all__ = [
    "ProjectCreateView", "ProjectListView", "ProjectDetailView", 
    "DependencyCreateView", "InitiateProjectBuildView", "ProjectBuildListView",
    "ProjectBuildDetailView", "DependencyListView", "DependencyDetailView"
]

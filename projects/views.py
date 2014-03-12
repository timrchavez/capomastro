from django.views.generic import CreateView, ListView, DetailView, View
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from braces.views import (
    LoginRequiredMixin, PermissionRequiredMixin, FormValidMessageMixin,
    SuccessURLRedirectListMixin)

from projects.models import Project, Dependency, ProjectDependency
from projects.forms import ProjectForm
from projects.helpers import build_project


class ProjectCreateView(
    LoginRequiredMixin, PermissionRequiredMixin,
    SuccessURLRedirectListMixin, FormValidMessageMixin, CreateView):

    permission_required = "projects.add_project"
    success_list_url = "projects_index"
    form_valid_message = "Project created"
    model = Project
    form_class = ProjectForm


class ProjectListView(LoginRequiredMixin, ListView):

    model = Project


class ProjectBuildView(LoginRequiredMixin, View):

    def post(self, request, pk):
        project = Project.objects.get(pk=pk)
        project_build = build_project(project)
        messages.add_message(
            request, messages.INFO, "Build '%s' Queued." % project_build.build_id)
        return HttpResponseRedirect(reverse("projects_index"))


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
    LoginRequiredMixin, PermissionRequiredMixin,
    SuccessURLRedirectListMixin, FormValidMessageMixin, CreateView):

    model = Dependency
    fields = ["name", "dependency_type"]


__all__ = [
    "ProjectCreateView", "ProjectListView", "ProjectDetailView", 
    "DependencyCreateView", "ProjectBuildView"]

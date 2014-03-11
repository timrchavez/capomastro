from django.views.generic import CreateView, ListView, DetailView
from braces.views import (
    LoginRequiredMixin, PermissionRequiredMixin, FormValidMessageMixin,
    SuccessURLRedirectListMixin)

from projects.models import Project, Dependency, ProjectDependency
from projects.forms import ProjectForm


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
    "DependencyCreateView"]

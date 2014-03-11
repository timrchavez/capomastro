from django.views.generic import CreateView, ListView, DetailView
from braces.views import (
    LoginRequiredMixin, PermissionRequiredMixin, FormValidMessageMixin,
    SuccessURLRedirectListMixin)

from projects.models import Project, Dependency
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


class DependencyCreateView(
    LoginRequiredMixin, PermissionRequiredMixin,
    SuccessURLRedirectListMixin, FormValidMessageMixin, CreateView):

    model = Dependency
    fields = ["name", "dependency_type"]


__all__ = [
    "ProjectCreateView", "ProjectListView", "ProjectDetailView", 
    "DependencyCreateView"]

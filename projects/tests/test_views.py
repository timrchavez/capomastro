import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_webtest import WebTest
import mock

from projects.models import ProjectDependency, Project, ProjectBuild
from .factories import ProjectFactory, DependencyFactory
from jenkins.tests.factories import BuildFactory, JobFactory

# TODO Introduce subclass of WebTest that allows easy assertions that a page
# requires various permissions...
# Possibly, through looking to see if Views are mixed in with the various
# Django-Braces mixins.


class ProjectDetailTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_user("testing")

    def test_page_requires_authenticated_user(self):
        """
        """
        # TODO: We should assert that requests without a logged in user
        # get redirected to login.

    def test_server_detail(self):
        """
        The detail view should render the server and jobs for the server.
        """
        project = ProjectFactory.create()
        # TODO: Work out how to configure DjangoFactory to setup m2m through
        dependency = ProjectDependency.objects.create(
            project=project, dependency=DependencyFactory.create())
        project_url = reverse("projects_detail", kwargs={"pk": project.pk})
        response = self.app.get(project_url, user="testing")

        self.assertEqual(200, response.status_code)
        self.assertEqual(project, response.context["project"])
        self.assertEqual([dependency], list(response.context["dependencies"]))


class ProjectCreateTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_superuser(
            "testing", "testing@example.com", "password")
        self.dependency1 = DependencyFactory.create()
        self.dependency2 = DependencyFactory.create()

    def test_page_requires_permission(self):
        """
        """
        # TODO: We should assert that requests without the
        # "projects.add_project" get redirected to login.

    def test_create_project_with_dependencies(self):
        """
        We can create projects with a set of dependencies.
        """
        project_url = reverse("projects_create")
        response = self.app.get(project_url, user="testing")
        form = response.forms["create-project"]
        form["dependencies"].select_multiple(
            [self.dependency1.pk, self.dependency2.pk])
        form["name"].value = "My Project"

        response = form.submit()

        project = Project.objects.get(name="My Project")
        # TODO: Check that the dependencies are not auto-tracked.

    def test_create_project_with_auto_track(self):
        """
        We can set the auto_track on dependencies of the project.
        """

    def test_create_project_non_unique_name(self):
        """
        The project name should be unique.
        """


class ProjectBuildViewTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_user("testing")

    def test_page_requires_authenticated_user(self):
        """
        """
        # TODO: We should assert that requests without a logged in user
        # get redirected to login.

    def test_build_project_view(self):
        """
        The detail view should render the server and jobs for the server.
        """
        project = ProjectFactory.create()
        dependency = ProjectDependency.objects.create(
            project=project, dependency=DependencyFactory.create())
        project_url = reverse("projects_detail", kwargs={"pk": project.pk})

        project_build = mock.MagicMock(autospec=ProjectBuild)
        project_build.build_id = "20140312.1"
        with mock.patch("projects.views.build_project") as mock_build_project:
            mock_build_project.return_value = project_build
            response = self.app.get(project_url, user="testing")
            response = response.forms["build-project"].submit().follow()

        mock_build_project.assert_called_once_with(project)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response, "Build '20140312.1' Queued.")


class ProjectBuildListViewTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_user("testing")

    def test_page_requires_authenticated_user(self):
        """
        """
        # TODO: We should assert that requests without a logged in user
        # get redirected to login.

    def test_project_build_list_view(self):
        """
        The detail view should render the server and jobs for the server.
        """
        job = JobFactory.create()
        BuildFactory.create_batch(5, job=job)

        project = ProjectFactory.create()

        dependency = ProjectDependency.objects.create(
            project=project, dependency=DependencyFactory.create(job=job))
        project_build = ProjectBuild.objects.create(project=project)
        builds = BuildFactory.create(job=job, build_id=project_build.build_id)

        url = reverse("projects_project_build_list", kwargs={"pk": project.pk})
        response = self.app.get(url, user="testing")

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            set([project_build]), set(response.context["project_builds"]))
        self.assertEqual(project, response.context["project"])

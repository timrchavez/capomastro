from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_webtest import WebTest
import mock

from projects.models import ProjectDependency, Project
from .factories import (
    ProjectFactory, DependencyFactory, ProjectBuildFactory)
from jenkins.tests.factories import (
    BuildFactory, JobFactory, JobTypeFactory, JenkinsServerFactory)

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
        project_url = reverse("project_detail", kwargs={"pk": project.pk})
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
        project_url = reverse("project_create")
        response = self.app.get(project_url, user="testing")
        form = response.forms["create-project"]
        form["dependencies"].select_multiple(
            [self.dependency1.pk, self.dependency2.pk])
        form["name"].value = "My Project"

        response = form.submit()

        project = Project.objects.get(name="My Project")
        dependencies = ProjectDependency.objects.filter(project=project)

        self.assertEqual(
            [False, False],
            list(dependencies.values_list("auto_track", flat=True)))
        self.assertEqual(
            set([self.dependency1.name, self.dependency2.name]),
            set(dependencies.values_list("dependency__name", flat=True)))

    def test_create_project_with_auto_track(self):
        """
        We can set the auto_track on dependencies of the project.
        """
        project_url = reverse("project_create")
        response = self.app.get(project_url, user="testing")
        form = response.forms["create-project"]
        form["dependencies"].select_multiple(
            [self.dependency1.pk, self.dependency2.pk])
        form["name"].value = "My Project"
        form["auto_track"].value = True

        response = form.submit()

        project = Project.objects.get(name="My Project")
        dependencies = ProjectDependency.objects.filter(project=project)

        self.assertEqual(
            [True, True],
            list(dependencies.values_list("auto_track", flat=True)))

    def test_create_project_non_unique_name(self):
        """
        The project name should be unique.
        """
        ProjectFactory.create(name="My Project")

        project_url = reverse("project_create")
        response = self.app.get(project_url, user="testing")
        form = response.forms["create-project"]
        form["dependencies"].select_multiple(
            [self.dependency1.pk])
        form["name"].value = "My Project"

        response = form.submit()
        self.assertContains(response, "Project with this Name already exists.")


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
        ProjectDependency.objects.create(
            project=project, dependency=DependencyFactory.create())
        project_url = reverse("project_detail", kwargs={"pk": project.pk})

        projectbuild = ProjectBuildFactory.create(project=project)
        with mock.patch("projects.views.build_project") as mock_build_project:
            mock_build_project.return_value = projectbuild
            response = self.app.get(project_url, user="testing")
            response = response.forms["build-project"].submit().follow()

        mock_build_project.assert_called_once_with(project, user=self.user)
        self.assertEqual(200, response.status_code)

        self.assertEqual(
            "Project Build %s" % projectbuild.build_id,
            response.html.title.text)
        self.assertContains(
            response, "Build '%s' Queued." % projectbuild.build_id)


class ProjectBuildListViewTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_user("testing")

    def test_page_requires_authenticated_user(self):
        """
        """
        # TODO: We should assert that requests without a logged in user
        # get redirected to login.

    def test_projectbuild_list_view(self):
        """
        The detail view should render the server and jobs for the server.
        """
        job = JobFactory.create()
        BuildFactory.create_batch(5, job=job)

        project = ProjectFactory.create()

        ProjectDependency.objects.create(
            project=project, dependency=DependencyFactory.create(job=job))
        projectbuild = ProjectBuildFactory.create(project=project)
        BuildFactory.create(job=job, build_id=projectbuild.build_id)

        url = reverse("project_projectbuild_list", kwargs={"pk": project.pk})
        response = self.app.get(url, user="testing")

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            set([projectbuild]), set(response.context["projectbuilds"]))
        self.assertEqual(project, response.context["project"])

    def test_projectbuild_list_view(self):
        """
        The detail view should render the server and jobs for the server.
        """
        job = JobFactory.create()
        BuildFactory.create_batch(5, job=job)

        project = ProjectFactory.create()

        ProjectDependency.objects.create(
            project=project, dependency=DependencyFactory.create(job=job))
        projectbuild = ProjectBuildFactory.create(project=project)
        BuildFactory.create(job=job, build_id=projectbuild.build_id)

        url = reverse("project_projectbuild_list", kwargs={"pk": project.pk})
        response = self.app.get(url, user="testing")

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            set([projectbuild]), set(response.context["projectbuilds"]))
        self.assertEqual(project, response.context["project"])


class DependencyListViewTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_user("testing")

    def test_page_requires_authenticated_user(self):
        """
        """
        # TODO: We should assert that requests without a logged in user
        # get redirected to login.

    def test_dependency_list_view(self):
        """
        The Dependency List should render a list of dependencies with links to
        their type detail views.
        """
        dependencies = DependencyFactory.create_batch(5)
        url = reverse("dependency_list")
        response = self.app.get(url, user="testing")

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            set(dependencies), set(response.context["dependencies"]))

        response = response.click(dependencies[0].job.jobtype.name)
        self.assertEqual(
            dependencies[0].job.jobtype.name, response.html.title.text)


class DependencyCreateTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_superuser(
            "testing", "testing@example.com", "password")
        self.jobtype = JobTypeFactory.create(
            config_xml="this is the job xml")
        self.server = JenkinsServerFactory.create()

    def test_page_requires_permission(self):
        """
        """
        # TODO: We should assert that requests without the
        # "projects.add_dependency" get redirected to login.

    def test_create_dependency(self):
        """
        We can create dependencies with jobs in servers.
        """
        project_url = reverse("dependency_create")
        response = self.app.get(project_url, user="testing")

        form = response.forms["dependency-form"]
        form["job_type"].select(self.jobtype.pk)
        form["server"].select(self.server.pk)
        form["name"].value = "My Dependency"

        response = form.submit().follow()

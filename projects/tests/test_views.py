import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_webtest import WebTest
from mock import patch

from projects.models import ProjectDependency
from .factories import ProjectFactory, DependencyFactory


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
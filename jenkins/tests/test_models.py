from django.test import TestCase

from httmock import HTTMock
from jenkinsapi.jenkins import Jenkins

from jenkins.models import Build
from .factories import BuildFactory, JenkinsServerFactory
from .helpers import mock_url


class JenkinsServerTest(TestCase):

    def test_get_client(self):
        """
        JenkinsServer.get_client should return a Jenkins client configured
        appropriately.
        """
        server = JenkinsServerFactory.create()

        mock_request = mock_url(
            r"\/api\/python$", "fixture1")
        with HTTMock(mock_request):
            client = server.get_client()
        self.assertIsInstance(client, Jenkins)


class BuildTest(TestCase):

    def test_ordering(self):
        """Builds should be ordered in reverse build order by default."""
        builds = BuildFactory.create_batch(5)
        build_numbers = sorted([x.number for x in builds], reverse=True)

        self.assertEqual(
            build_numbers,
            list(Build.objects.all().values_list("number", flat=True)))

from django.test import TestCase
from django.utils import timezone

from httmock import HTTMock
import mock
from jenkinsapi.jenkins import Jenkins

from jenkins.models import Build, JobType, generate_job_name
from .helpers import mock_url
from .factories import (
    BuildFactory, JenkinsServerFactory, JobTypeFactory, JobFactory)


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


class JobTypeTest(TestCase):

    def test_instantiation(self):
        """We can create JobTypes."""
        jobtype = JobType.objects.create(
            name="my-test", config_xml="testing xml")


class JobTest(TestCase):

    def test_generate_job_name(self):
        """
        generate_job_name should generate a name for the job on the server.
        """
        job = JobFactory.create()
        now  = timezone.now()

        with mock.patch("jenkins.models.timezone") as timezone_mock:
            timezone_mock.now.return_value = now
            name = generate_job_name(job)
        expected_job_name = "%s_%d" % (job.name, int(now.toordinal()))
        self.assertEqual(name, expected_job_name)

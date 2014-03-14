from django.test import TestCase
from django.test.utils import override_settings

from httmock import HTTMock
from jenkinsapi.jenkins import Jenkins

from jenkins.models import Build, JobType
from .factories import BuildFactory, JenkinsServerFactory, JobTypeFactory
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


template_config = """
<?xml version='1.0' encoding='UTF-8'?>
<project><description>{{ dependency.description }}</description>
</project>"
"""

class JobTypeTest(TestCase):

    def test_instantiation(self):
        """We can create JobTypes."""
        jobtype = JobType.objects.create(
            name="my-test", config_xml="testing xml")

#    def test_generate_config_for_dependency(self):
#        """
#        We can use Django templating in the config.xml and this will be
#        interpreted correctly.
#        """
#        jobtype = JobTypeFactory.create(
#            config_xml=template_config)
#        dependency = DependencyFactory.create()
#        job_xml = jobtype.generate_config_for_dependency(dependency)
#        self.assertIn(dependency.description, job_xml)
#
#    @override_settings(NOTIFICATION_HOST="http://example.com")
#    def test_generate_config_for_dependency_provides_notification_host(self):
#        """
#        """
#        jobtype = JobTypeFactory.create(
#            config_xml="{{ notification_host }}")
#        dependency = DependencyFactory.create()
#        job_xml = jobtype.generate_config_for_dependency(dependency)
#        self.assertEqual("http://example.com/jenkins/notifications/", job_xml)

import logging

from django.test import TestCase

import mock
import jenkinsapi.job

from jenkins.helpers import import_build_for_job
from jenkins.models import Build
from .factories import JobFactory, BuildFactory


class ImportBuildForJobTest(TestCase):

    def test_import_build_for_job(self):
        """
        Import build for job should update the build with the details fetched
        from the Jenkins server, including fetching the artifact details.
        """
        job = JobFactory.create()
        build = BuildFactory.create(job=job, number=5)

        mock_job = mock.Mock(spec=jenkinsapi.job.Job)
        mock_build = mock.Mock(_data={"duration": 1000})

        mock_job.get_build.return_value = mock_build

        mock_build.get_status.return_value = "SUCCESS"
        mock_build.get_result_url.return_value = "http://localhost/123"
        mock_build.get_artifacts.return_value = []

        with mock.patch("jenkins.helpers.logging") as mock_logging:
            with mock.patch("jenkins.models.Jenkins") as mock_jenkins:
                mock_jenkins.return_value.get_job.return_value = mock_job
                import_build_for_job(job.pk, 5)

        mock_jenkins.assert_called_with(
            job.server.url, username=u"root", password=u"testing")

        mock_logging.assert_has_calls(
            [mock.call.info("Located job testjob%d\n" % job.pk),
             mock.call.info("Using server at http://www%d.example.com/\n" % job.server.pk),
             mock.call.info("{'status': 'SUCCESS', 'duration': 1000, 'url': 'http://localhost/123'}")])

        build = Build.objects.get(pk=build.pk)
        self.assertEqual(1000, build.duration)
        self.assertEqual("SUCCESS", build.status)

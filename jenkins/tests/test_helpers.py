from django.test import TestCase

import mock
import jenkinsapi.job

from jenkins.helpers import import_build_for_job, create_job
from jenkins.models import Build, Job
from .factories import (
    JobFactory, BuildFactory, JobTypeFactory, JenkinsServerFactory)


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
            [mock.call.info("Located job %s\n" % job),
             mock.call.info("Using server at %s\n" % job.server.url),
             mock.call.info("{'status': 'SUCCESS', 'duration': 1000, 'url': 'http://localhost/123'}")])

        build = Build.objects.get(pk=build.pk)
        self.assertEqual(1000, build.duration)
        self.assertEqual("SUCCESS", build.status)


class CreateJobTest(TestCase):

    def test_create_job(self):
        """
        Create job should instantiate a job associated with a server generate a
        name for the job.
        """
        jobtype = JobTypeFactory.create()
        server = JenkinsServerFactory.create()

        with mock.patch("jenkins.helpers.generate_job_name") as mock_name:
            mock_name.return_value = "known name"
            create_job(jobtype, server)

        job = Job.objects.get(jobtype=jobtype, server=server)
        self.assertEqual("known name", job.name)

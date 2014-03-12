import logging

from django.test import TestCase
from django.test.utils import override_settings

from mock import patch, call

from jenkins.tasks import build_job
from jenkins.models import JenkinsServer
from .factories import JobFactory, JenkinsServerFactory, BuildFactory


class BuildJobTaskTest(TestCase):

    def setUp(self):
        self.server = JenkinsServerFactory.create()

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_build_job(self):
        """
        The build_job task should find the associated server, and request that
        the job be built.
        """
        job = JobFactory.create(server=self.server)
        with patch("jenkins.models.Jenkins", spec=True) as mock_jenkins:
            build_job(job.pk)

        mock_jenkins.assert_called_with(
            self.server.url, username=u"root", password=u"testing")
        mock_jenkins.return_value.build_job.assert_called_with(
            job.name, params={})

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_build_job_with_build_id(self):
        """
        If we provide a build_id, this should be sent as parameter.
        """
        job = JobFactory.create(server=self.server)
        with patch("jenkins.models.Jenkins", spec=True) as mock_jenkins:
            build_job(job.pk, "20140312.1")

        mock_jenkins.assert_called_with(
            self.server.url, username=u"root", password=u"testing")
        mock_jenkins.return_value.build_job.assert_called_with(
            job.name, params={"BUILD_ID": "20140312.1"})


class ImportBuildTaskTest(TestCase):
    pass
    # TODO: This needs written...

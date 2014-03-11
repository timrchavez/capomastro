import json

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_webtest import WebTest
from mock import patch

from jenkins.views import NotificationHandlerView
from jenkins.models import Build
from .factories import JobFactory, JenkinsServerFactory, BuildFactory


class NotificationHandlerTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = NotificationHandlerView.as_view()
        self.server = JenkinsServerFactory.create()
        self.job = JobFactory(server=self.server, name="mytestjob")

    def _get_response_with_data(self, data, remote_addr=None):
        request = self.factory.post(
            "/jenkins/notifications", content_type="application/json",
            data=json.dumps(data),
            REMOTE_ADDR=remote_addr or self.server.remote_addr)
        return self.view(request)

    def test_handle_notification_with_unknown_remote_addr(self):
        """
        If we can't find the JenkinsServer using the remote_addr supplied in the
        request we should get a 412 response and log this.
        """
        notification = {}
        with patch("jenkins.views.logging") as mock_logging:
            response = self._get_response_with_data(
                notification, remote_addr="127.0.0.1")
            self.assertEqual(412, response.status_code)
            mock_logging.warn.assert_called_once_with(
                "Could not find server with REMOTE_ADDR: 127.0.0.1")

    def test_handle_notification_with_unknown_job(self):
        """
        If we can't find the job referred to in the notification, we should get
        a 404 response?

        NOTE: The Jenkins notification plugin doesn't seem to care what response
        we send back...
        """
        notification = {"name": "unknown job", "build": {"phase": "FINISHED"}}
        with patch("jenkins.views.logging") as mock_logging:
            response = self._get_response_with_data(
                notification)
            self.assertEqual(412, response.status_code)
            mock_logging.warn.assert_called_once_with(
                "Notification for unknown job 'unknown job'")

    def test_handle_started_notification(self):
        """
        When a build starts we get a STARTED notification.
        """
        started = {
            "build": {
                "number": 11,
                "phase": "STARTED",
                "url": "job/mytestjob/11/"},
            "name": "mytestjob",
            "url": "job/mytestjob/"}
        response = self._get_response_with_data(started)
        # TODO: We should create a build and use this to determine whether or
        # not we have a current build in progress.
        self.assertEqual(0, Build.objects.count())

    def test_handle_completed_notification(self):
        """
        When a build starts we get a COMPLETED notification, we should not
        create a build for this phase.
        """
        completed = {
            "build": {
                 "number": 11,
                 "phase": "COMPLETED",
                 "status": "SUCCESS",
                 "url": "job/mytestjob/11/"},
                 "name": "mytestjob",
                 "url": "job/mytestjob/"}
        response = self._get_response_with_data(completed)
        self.assertEqual(0, Build.objects.count())

    def test_handle_finished_notification(self):
        """
        When a build has completed all the post-build operations, we get a
        FINISHED notification, this should trigger creation of a Build
        representing the FINISHED build.
        """
        finished = {
            "build": {
                 "number": 11,
                 "phase": "FINISHED",
                 "status": "SUCCESS",
                 "url": "job/mytestjob/11/"},
                 "name": "mytestjob",
                 "url": "job/mytestjob/"}
        response = self._get_response_with_data(finished)
        build = Build.objects.get(job=self.job, number=11)
        self.assertEqual("SUCCESS", build.result)
        # TODO: This should be normalised to the Server URL.
        # Implement a JenkinsServer.normalise_url method.
        self.assertEqual("job/mytestjob/11/", build.url)
        self.assertEqual("FINISHED", build.phase)


class JenkinsServerIndexTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_user("testing")

    def test_page_requires_authenticated_user(self):
        """
        """
        # TODO: We should assert that requests without a logged in user
        # get redirected to login.

    def test_server_index(self):
        """
        The index view should list all servers.
        """
        servers = JenkinsServerFactory.create_batch(5)
        response = self.app.get(reverse("jenkinsserver_index"), user="testing")
        self.assertEqual(200, response.status_code)
        self.assertEqual(servers, list(response.context["object_list"]))


class JenkinsServerDetailTest(WebTest):

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
        server = JenkinsServerFactory.create()
        jobs = JobFactory.create_batch(5, server=server)
        server_url = reverse("jenkinsserver_detail", kwargs={"pk": server.pk})
        response = self.app.get(server_url, user="testing")
        self.assertEqual(200, response.status_code)
        self.assertEqual(server, response.context["server"])
        self.assertEqual(jobs, list(response.context["jobs"]))


#class JobIndexTest(WebTest):
#
#    def setUp(self):
#        self.user = User.objects.create_user("testing")
#
#    def test_server_index(self):
#        """
#        The index view should list all servers.
#        """
#        servers = JenkinsServerFactory.create_batch(5)
#        response = self.app.get(reverse("jenkinsserver_index"), user="testing")
#        self.assertEqual(200, response.status_code)
#        self.assertEqual(servers, list(response.context["object_list"]))


class ServerJobBuildIndexTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_user("testing")

    def test_page_requires_authenticated_user(self):
        """
        """
        # TODO: We should assert that requests without a logged in user
        # get redirected to login.

    def test_server_job_build_index(self):
        """
        The detail view should render the server, job and builds.
        """
        server = JenkinsServerFactory.create()
        job = JobFactory.create(server=server)
        builds = BuildFactory.create_batch(5, job=job)
        server_url = reverse(
            "jenkinsserver_job_builds_index",
            kwargs={"server_pk": server.pk, "job_pk": job.pk})
        response = self.app.get(server_url, user="testing")
        self.assertEqual(200, response.status_code)
        self.assertEqual(server, response.context["server"])
        self.assertEqual(job, response.context["job"])
        self.assertEqual(set(builds), set(response.context["builds"]))

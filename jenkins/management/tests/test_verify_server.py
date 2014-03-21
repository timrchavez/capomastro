from django.test import TestCase

import mock
from jenkinsapi import jenkins
from requests.exceptions import HTTPError

from jenkins.management.helpers import verify_jenkinsserver
from jenkins.tests.factories import JenkinsServerFactory


class VerifyServerTest(TestCase):

    def test_verify_server(self):
        """
        Verify a server setup for use with Capomastro.
        """
        server = JenkinsServerFactory.create()

        # TODO: This is a fragile test because it doesn't completely mock out
        # the Plugins object that's returned by get_plugins.
        with mock.patch(
                "jenkins.models.Jenkins",
                spec=jenkins.Jenkins) as mock_jenkins:
            messages = verify_jenkinsserver(server)

        mock_jenkins.assert_called_with(
            server.url, username=u"root", password=u"testing")
        mock_jenkins.return_value.get_plugins.assert_called_once()

        self.assertEqual(
            ["Missing plugins: notification"], messages)

    def test_verify_server_with_authentication_error(self):
        """
        Verify a server setup for use with Capomastro.
        """
        server = JenkinsServerFactory.create()

        with mock.patch(
                "jenkins.models.Jenkins",
                spec=jenkins.Jenkins) as mock_jenkins:
            error = HTTPError(401, "No authentication")
            mock_jenkins.side_effect = error
            messages = verify_jenkinsserver(server)

        mock_jenkins.assert_called_with(
            server.url, username=u"root", password=u"testing")
        self.assertEqual(
            ["ERROR: [Errno 401] No authentication"], messages)

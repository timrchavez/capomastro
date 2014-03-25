from __future__ import unicode_literals

from cStringIO import StringIO

from django.core.management.base import CommandError
from django.test import TestCase

from jenkins.management.helpers import import_jenkinsserver
from jenkins.models import JenkinsServer
from jenkins.tests.factories import JenkinsServerFactory


class ImportJenkinsServerTest(TestCase):

    def test_import_jenkinsserver(self):
        """
        We can import a new keypair with a name.
        """
        stdout = StringIO()
        import_jenkinsserver(
            "server1", "http://example.com/", "admin", "testing",
            "192.168.1.2", stdout=stdout)

        server = JenkinsServer.objects.get(name="server1")
        self.assertEqual("http://example.com/", server.url)
        self.assertEqual("admin", server.username)
        self.assertEqual("testing", server.password)
        self.assertEqual("192.168.1.2", server.remote_addr)

        self.assertEqual("Server created\n", stdout.getvalue())

    def test_import_jenkinsserver_fails_with_preexisting_name(self):
        """
        import_jenkinsserver should fail if we have a server with that name.
        """
        server = JenkinsServerFactory.create(
            name="testing", url="http://example.com/")
        with self.assertRaises(CommandError) as cm:
          import_jenkinsserver(
              "testing", "http://example.com/2", "admin",
              "password", "192.168.2.2")

        self.assertEqual("Server already exists", str(cm.exception))

        server = JenkinsServer.objects.get(name=server.name)
        self.assertEqual("http://example.com/", server.url)
        self.assertEqual("root", server.username)
        self.assertEqual("testing", server.password)
        self.assertEqual("192.168.50.201", server.remote_addr)

    def test_import_jenkinsserver_updates_existing_server(self):
        """
        import_jenkinsserver should update update the details if we supply the
        update parameter.
        """
        stdout = StringIO()
        server = JenkinsServerFactory.create()
        import_jenkinsserver(
            server.name, "http://www1.example.com/", "admin", "secret",
            "192.168.2.2", update=True, stdout=stdout)

        server = JenkinsServer.objects.get(name=server.name)
        self.assertEqual("http://www1.example.com/", server.url)
        self.assertEqual("admin", server.username)
        self.assertEqual("secret", server.password)
        self.assertEqual("192.168.2.2", server.remote_addr)
        self.assertEqual("Server updated\n", stdout.getvalue())

from django.test import TestCase

from archives.models import Archive
from archives.policies import CdimageArchivePolicy
from archives.archivers import SshArchiver

from credentials.tests.factories import SshKeyPairFactory
from .factories import ArchiveFactory


class ArchiveTest(TestCase):
    def setUp(self):
        self.credentials = SshKeyPairFactory.create()

    def test_instantiation(self):
        """We can instantiate an Archive."""
        archive = Archive.objects.create(
            name="My Test Archive",
            host="archive.example.com",
            policy="cdimage",
            transport="ssh",
            basedir="/var/tmp",
            username="testing",
            ssh_credentials=self.credentials)

    def test_get_archiver(self):
        """
        Archive.get_transport should return the class to be used when moving
        files to an archive store.
        """
        archive = ArchiveFactory.create(transport="ssh")
        self.assertEqual(SshArchiver, archive.get_archiver())

    def test_get_policy(self):
        """
        Archive.get_policy should return the class to be used when deciding the
        names for files in the archive store.
        """
        archive = ArchiveFactory.create(policy="cdimage")
        self.assertEqual(CdimageArchivePolicy, archive.get_policy())

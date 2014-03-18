import mock
from django.test import TestCase

from archives.archivers import Archiver


class LoggingArchiver(Archiver):
    """
    Test archiver that just logs the calls the Archiver
    code makes.
    """
    log = []
    def start(self):
        self.log.append("START")

    def end(self):
        self.log.append("END")

    def archive_artifact(self, url, mapped):
        self.log.append("%s -> %s" % (url, mapped))


class ArchiverTest(TestCase):
    def test_archiver_sequence(self):
        """
        The start code is called before archiving each
        mapping, then the end code is called.
        """
        policy = mock.Mock()
        policy.get_mappings()
        policy.get_mappings.return_value = {
            "/path/1/": "mapped/path/1/"
        }
        archiver = LoggingArchiver(policy, None)
        archiver.archive()
        self.assertEqual(
            ["START", "/path/1/ -> mapped/path/1/", "END"],
            archiver.log)

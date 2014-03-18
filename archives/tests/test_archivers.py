import mock
from django.test import TestCase

from archives.archivers import Archiver, SshArchiver


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


class SshArchiverTest(TestCase):
    def test_ssh_and_sftp_clients_used(self):
        """
        The SSHClient and SFTPClient should be used to
        transport artifacts.
        """
        mock_policy = mock.Mock()
        mock_policy.get_mappings()
        mock_policy.get_mappings.return_value = {
            "/path/1/": "mapped/path/1/"
        }
        mock_target = mock.Mock()
        mock_target.basedir = "/var/www"
        mock_target.host = "archive.ubuntu.com"
        mock_target.ssh_credentials.get_pkey()
        mock_target.ssh_credentials.get_pkey.return_value = mock.Mock()

        manager = mock.Mock()

        with mock.patch("archives.archivers.SSHClient") as mock_client:
            with mock.patch("archives.archivers.SFTPClient") as mock_sftp:
                with mock.patch("archives.archivers.urllib2") as mock_urllib2:
                    manager.attach_mock(mock_client, "client")
                    manager.attach_mock(mock_sftp, "sftp")
                    manager.attach_mock(mock_urllib2, "urllib2")
                    mock_urllib2.return_value = manager.urllib2
                    mock_client.return_value.exec_command.return_value = (
                        None, mock.Mock(), None)
                    archiver = SshArchiver(mock_policy, mock_target)
                    archiver.archive()

        expected_calls = [
            # ssh client gets set up
            mock.call.client(),
            mock.call.client().set_missing_host_key_policy(mock.ANY),
            # connect to the target archive
            mock.call.client().connect(
                'archive.ubuntu.com',
                pkey=mock_target.ssh_credentials.get_pkey()),
            mock.call.client().get_transport(),
            mock.call.sftp.from_transport(mock.ANY),
            # init the remote directory structure
            mock.call.client().exec_command(
                'mkdir -p `dirname /var/www/mapped/path/1/`'),
            # upload the file
            mock.call.urllib2.urlopen('/path/1/'),
            mock.call.sftp.from_transport().stream_file_to_remote(
                mock_urllib2.urlopen(), '/var/www/mapped/path/1/'),
            mock.call.client().close()]
        manager.assert_has_calls(expected_calls)

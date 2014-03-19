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

    def _get_mock_policy_and_target(self):
        """
        Helper for generating a mock policy and archive target.
        """
        mock_policy = mock.Mock()
        mock_policy.get_mappings()
        mock_policy.get_mappings.return_value = {
            "/path/1/": "mapped/path/1/"
        }
        mock_target = mock.Mock()
        mock_target.basedir = "/var/www"
        mock_target.host = "archive.example.com"
        mock_target.ssh_credentials.get_pkey()
        mock_target.ssh_credentials.get_pkey.return_value = mock.Mock()

        return (mock_policy, mock_target)

    def _get_archiver_and_mocks(self, manager, policy, target):
        """
        Get an archiver, loaded with mocks.
        """
        with mock.patch("archives.archivers.SSHClient") as mock_client:
            with mock.patch("archives.archivers.SFTPClient") as mock_sftp:
                with mock.patch("archives.archivers.urllib2") as mock_urllib2:
                    manager.attach_mock(mock_client, "client")
                    manager.attach_mock(mock_sftp, "sftp")
                    manager.attach_mock(mock_urllib2, "urllib2")
                    mock_urllib2.return_value = manager.urllib2
                    mock_client.return_value.exec_command.return_value = (
                        None, mock.Mock(), None)
                    mock_client.return_value.get_transport.return_value = "TRANSPORT"
                    archiver =  SshArchiver(policy, target)
                    archiver.archive()
                    return (archiver, mock_client, mock_sftp, mock_urllib2)
                    
    def test_ssh_client_connects_to_target(self):
        """
        The SSHClient should connect to the host specified by the
        archive target.
        """
        mock_policy, mock_target = self._get_mock_policy_and_target()
        manager = mock.Mock()
        archiver, mock_client, mock_sftp, mock_urllib2 = self._get_archiver_and_mocks(
            manager, mock_policy, mock_target)
        expected_calls = [
            # ssh client gets set up
            mock.call.client(),
            mock.call.client().set_missing_host_key_policy(mock.ANY),
            # connect to the target archive
            mock.call.client().connect(
                'archive.example.com',
                pkey=mock_target.ssh_credentials.get_pkey())]

        manager.assert_has_calls(expected_calls)

    def test_sftp_client_loaded_with_ssh_client_transport(self):
        """
        The sftp client should use the ssh client's transport.
        """
        mock_policy, mock_target = self._get_mock_policy_and_target()
        manager = mock.Mock()
        archiver, mock_client, mock_sftp, mock_urllib2 = self._get_archiver_and_mocks(
            manager, mock_policy, mock_target)
        expected_calls = [
            mock.call.client().get_transport(),
            mock.call.sftp.from_transport("TRANSPORT")]
        manager.assert_has_calls(expected_calls)

    def test_remote_directory_structure_is_initialized(self):
        """
        A command is set through the ssh client to create the
        base directory for the file to be uploaded.
        """
        mock_policy, mock_target = self._get_mock_policy_and_target()
        manager = mock.Mock()
        archiver, mock_client, mock_sftp, mock_urllib2 = self._get_archiver_and_mocks(
            manager, mock_policy, mock_target)
        expected_calls = [
            mock.call.client().exec_command(
                "mkdir -p `dirname /var/www/mapped/path/1/`"), ]
        manager.assert_has_calls(expected_calls)

    def test_file_is_read_and_sent_over_sftp(self):
        """
        The remote artifact is read using urllib2 and
        sent over sftp.
        """
        mock_policy, mock_target = self._get_mock_policy_and_target()
        manager = mock.Mock()
        archiver, mock_client, mock_sftp, mock_urllib2 = self._get_archiver_and_mocks(
            manager, mock_policy, mock_target)
        expected_calls = [
            mock.call.urllib2.urlopen('/path/1/'),
            mock.call.sftp.from_transport().stream_file_to_remote(
                mock_urllib2.urlopen(), '/var/www/mapped/path/1/')]
        manager.assert_has_calls(expected_calls)

    def test_ssh_client_gets_closed(self):
        """
        The ssh client's connection gets closed.
        """
        mock_policy, mock_target = self._get_mock_policy_and_target()
        manager = mock.Mock()
        archiver, mock_client, mock_sftp, mock_urllib2 = self._get_archiver_and_mocks(
            manager, mock_policy, mock_target)
        expected_calls = [mock.call.client().close(), ]
        manager.assert_has_calls(expected_calls)

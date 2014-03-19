import mock
from django.test import TestCase

from archives.policies import ArchivePolicy, CdimageArchivePolicy


class ArchivePolicyTest(TestCase):
    def test_mappings_from_project_build_artifacts(self):
        """
        The default archive policy should return the urls
        from the build artifacts.
        """
        mock_build = mock.Mock()
        mock_artifact_1 = mock.Mock()
        mock_artifact_1.url = "/first/path/"
        mock_artifact_2 = mock.Mock()
        mock_artifact_2.url = "/second/path/"
        mock_build.get_current_artifacts()
        mock_build.get_current_artifacts.return_value = [
            mock_artifact_1, mock_artifact_2]

        policy = ArchivePolicy(project_build=mock_build)
        mappings = policy.get_mappings()
        expected = {
            "/first/path/": "/first/path/",
            "/second/path/": "/second/path/"
        }
        self.assertEqual(expected, mappings)


class CdimageArchivePolicyTest(TestCase):
    def test_mappings_into_cdimage_structure(self):
        """
        Artifact paths and filenames are translated into
        a cdimage-like path, using the project name and
        build id.
        """
        mock_build = mock.Mock()
        mock_build.project.name = "my-project"
        mock_build.build_id = "20010101.0"
        mock_artifact_1 = mock.Mock()
        mock_artifact_1.url = "/first/path/thing.txt"
        mock_artifact_1.filename = "thing.txt"
        mock_artifact_2 = mock.Mock()
        mock_artifact_2.url = "/second/path/stuff.txt"
        mock_artifact_2.filename = "stuff.txt"
        mock_build.get_current_artifacts()
        mock_build.get_current_artifacts.return_value = [
            mock_artifact_1, mock_artifact_2]

        policy = CdimageArchivePolicy(project_build=mock_build)
        mappings = policy.get_mappings()
        expected = {
            "/first/path/thing.txt": "my-project/20010101.0/thing.txt",
            "/second/path/stuff.txt": "my-project/20010101.0/stuff.txt"
        }
        self.assertEqual(expected, mappings)
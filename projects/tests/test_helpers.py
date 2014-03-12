from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings

import mock

from projects.models import ProjectBuild, ProjectDependency
from projects.helpers import DefaultSettings, build_project
from .factories import ProjectFactory, JobFactory, DependencyFactory


class DefaultSettingsTest(SimpleTestCase):

    def test_default_values(self):
        """
        Anything we put in the configuration is available as a property on the
        settings object.
        """
        settings = DefaultSettings({"SERVER_HOST": "testing"})
        self.assertEqual("testing", settings.SERVER_HOST)

    def test_missing_value(self):
        """
        We should get an attribute error if there is no setting for a value.
        """
        settings = DefaultSettings({})
        with self.assertRaises(AttributeError) as cm:
            settings.MY_UNKNOWN_VALUE

        self.assertEqual(
            "'_defaults' object has no attribute 'MY_UNKNOWN_VALUE'",
            str(cm.exception))

    def test_get_value_or_none(self):
        """
        DefaultSettings.get_value_or_none should return None if there is no
        value or if it's None.
        """
        settings = DefaultSettings({"MY_VALUE": None})

        self.assertIsNone(settings.get_value_or_none("MY_TEST_VALUE"))
        self.assertIsNone(settings.get_value_or_none("MY_VALUE"))


class BuildProjectTest(TestCase):

    def test_build_project(self):
        """
        build_project should create build dependencies for each of the project
        dependencies and schedule builds of each.
        """
        project = ProjectFactory.create()
        dependency1 = DependencyFactory.create()
        project_dependency = ProjectDependency.objects.create(
            project=project, dependency=dependency1)

        dependency2 = DependencyFactory.create()
        project_dependency = ProjectDependency.objects.create(
            project=project, dependency=dependency2)

        with mock.patch("projects.helpers.build_job") as mock_build_job:
            new_build = build_project(project)
            self.assertIsInstance(new_build, ProjectBuild)

        mock_build_job.delay.assert_has_calls(
            [mock.call(dependency1.job.pk, new_build.build_id),
             mock.call(dependency2.job.pk, new_build.build_id)])

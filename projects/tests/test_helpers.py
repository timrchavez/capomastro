from django.test import TestCase
import mock

from projects.models import ProjectBuild, ProjectDependency
from projects.helpers import build_project
from .factories import ProjectFactory, DependencyFactory


class BuildProjectTest(TestCase):

    def test_build_project(self):
        """
        build_project should create build dependencies for each of the project
        dependencies and schedule builds of each.
        """
        project = ProjectFactory.create()
        dependency1 = DependencyFactory.create()
        ProjectDependency.objects.create(
            project=project, dependency=dependency1)

        dependency2 = DependencyFactory.create()
        ProjectDependency.objects.create(
            project=project, dependency=dependency2)

        with mock.patch("projects.helpers.build_job") as mock_build_job:
            new_build = build_project(project)
            self.assertIsInstance(new_build, ProjectBuild)

        mock_build_job.delay.assert_has_calls(
            [mock.call(dependency1.job.pk, new_build.build_id),
             mock.call(dependency2.job.pk, new_build.build_id)])

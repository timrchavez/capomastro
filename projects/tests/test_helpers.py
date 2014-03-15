from django.test import TestCase
import mock

from projects.models import (
    ProjectBuild, ProjectDependency, ProjectBuildDependency)
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

        build_dependencies = ProjectBuildDependency.objects.filter(
            projectbuild=new_build)
        self.assertEqual(2, build_dependencies.count())
        self.assertEqual(
            [dependency1.pk, dependency2.pk],
            list(build_dependencies.values_list("dependency", flat=True)))
        mock_build_job.delay.assert_has_calls(
            [mock.call(dependency1.job.pk, new_build.build_id),
             mock.call(dependency2.job.pk, new_build.build_id)])

    def test_build_project_with_no_queue_build(self):
        """
        If we pass queue_build = False to build_project, then no builds should
        happen.
        """
        project = ProjectFactory.create()
        dependency = DependencyFactory.create()
        ProjectDependency.objects.create(
            project=project, dependency=dependency)

        with mock.patch("projects.helpers.build_job") as mock_build_job:
            build_project(project)

        self.assertItemsEqual([], mock_build_job.call_args_list)

    def test_build_project_with_specified_dependencies(self):
        """
        If a list of dependencies is provided, then we should only build those
        dependencies.
        """
        [dep1, dep2, dep3] = DependencyFactory.create_batch(3)
        project = ProjectFactory.create()
        for dep in [dep1, dep2, dep3]:
            ProjectDependency.objects.create(
                project=project, dependency=dep)

        new_build = build_project(
            project, dependencies=[dep1, dep2], queue_build=False)

        projectbuild_dependencies = ProjectBuildDependency.objects.filter(
            projectbuild=new_build)
        self.assertEqual(2, projectbuild_dependencies.all().count())
        self.assertEqual(
            set([dep1, dep2]),
            set([x.dependency for x in projectbuild_dependencies.all()]))

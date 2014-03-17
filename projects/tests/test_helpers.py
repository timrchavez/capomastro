from django.test import TestCase
from django.contrib.auth.models import User
import mock

from projects.models import (
    ProjectBuild, ProjectDependency, ProjectBuildDependency)
from projects.helpers import build_project
from .factories import ProjectFactory, DependencyFactory
from jenkins.tests.factories import BuildFactory


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
                project=project, dependency=dep, auto_track=True)

        build = BuildFactory.create(job=dep1.job)
        # Reload object from database.
        project_dep1 = ProjectDependency.objects.get(
            project=project, dependency=dep1)
        self.assertEqual(build, project_dep1.current_build)


        with mock.patch("projects.helpers.build_job") as mock_build_job:
            new_build = build_project(project, dependencies=[dep1, dep2])

        projectbuild_dependencies = ProjectBuildDependency.objects.filter(
            projectbuild=new_build)
        self.assertEqual(3, projectbuild_dependencies.all().count())
        self.assertEqual(
            set([dep1, dep2, dep3]),
            set([x.dependency for x in projectbuild_dependencies.all()]))

        mock_build_job.delay.assert_has_calls(
            [mock.call(dep1.job.pk, new_build.build_id),
             mock.call(dep2.job.pk, new_build.build_id)])


    def test_build_project_assigns_user_correctly(self):
        """
        If we pass a user to build_project, the user is assigned as the user
        for the projectbuild.
        """
        user = User.objects.create_user("testing")
        project = ProjectFactory.create()
        dependency1 = DependencyFactory.create()
        ProjectDependency.objects.create(
            project=project, dependency=dependency1)

        new_build = build_project(project, user=user, queue_build=False)
        self.assertEqual(user, new_build.requested_by)

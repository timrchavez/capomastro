from django.test import TestCase

from .factories import ProjectFactory, DependencyFactory
from jenkins.tests.factories import BuildFactory
from projects.models import ProjectDependency
from projects.utils import get_build_table_for_project


class GetBuildTableForProjectTest(TestCase):

    def test_get_build_table_for_project_with_single_dependency(self):
        """
        We should get a table of rows for this dependency, indicating whether
        or not the current build is the build.
        """
        project = ProjectFactory.create()
        dependency = DependencyFactory.create()
        [build1, build2, build3, build4, build5] = BuildFactory.create_batch(
            5, job=dependency.job)
        ProjectDependency.objects.create(
            project=project, dependency=dependency, auto_track=False,
            current_build=build5)

        header, table = get_build_table_for_project(project)

        self.assertEqual([dependency], header)
        self.assertEqual([
            [{"build": build5, "current": True}],
            [{"build": build4, "current": False}],
            [{"build": build3, "current": False}],
            [{"build": build2, "current": False}],
            [{"build": build1, "current": False}]], table)

    def test_get_build_table_for_project_with_multiple_dependencies(self):
        """
        We should get a table of rows with all dependencies, indicating
        whether or not the current build is the build.
        """
        project = ProjectFactory.create()
        dependency1 = DependencyFactory.create()
        dependency2 = DependencyFactory.create()

        [build1, build2, build3, build4, build5] = BuildFactory.create_batch(
            5, job=dependency1.job)
        ProjectDependency.objects.create(
            project=project, dependency=dependency1, auto_track=False,
            current_build=build5)

        [build6, build7, build8, build9, build10] = BuildFactory.create_batch(
            5, job=dependency2.job)
        ProjectDependency.objects.create(
            project=project, dependency=dependency2, auto_track=False,
            current_build=build8)

        header, table = get_build_table_for_project(project)

        self.assertEqual([dependency1, dependency2], header)
        self.assertEqual([
            [{"build": build5, "current": True},
             {"build": build10, "current": False}],
            [{"build": build4, "current": False},
             {"build": build9, "current": False}],
            [{"build": build3, "current": False},
             {"build": build8, "current": True}],
            [{"build": build2, "current": False},
             {"build": build7, "current": False}],
            [{"build": build1, "current": False},
             {"build": build6, "current": False}]], table)

    def test_get_build_table_with_current_build_outside_recent(self):
        """
        If we have a current build outside the most recent 5, then we should
        extend the dependencies list for that row to illustrate the current
        build.
        """
        project = ProjectFactory.create()
        dependency = DependencyFactory.create()

        build = BuildFactory.create(job=dependency.job)
        [build1, build2, build3, build4, build5] = BuildFactory.create_batch(
            5, job=dependency.job)
        ProjectDependency.objects.create(
            project=project, dependency=dependency, auto_track=False,
            current_build=build)

        header, table = get_build_table_for_project(project)

        self.assertEqual([dependency], header)
        self.assertEqual([
            [{"build": build5, "current": False}],
            [{"build": build4, "current": False}],
            [{"build": build3, "current": False}],
            [{"build": build2, "current": False}],
            [{"build": build1, "current": False}],
            [{"build": build, "current": True}]], table)

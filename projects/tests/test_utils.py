from django.test import TestCase

from .factories import ProjectFactory, DependencyFactory
from jenkins.tests.factories import BuildFactory
from projects.models import ProjectDependency
from projects.utils import get_build_table_for_project


class GetBuildTableForProjectTest(TestCase):

    def test_get_build_table_for_project(self):
        """
        """
        project = ProjectFactory.create()
        dependency = DependencyFactory.create()
        [build1, build2, build3, build4, build5] = BuildFactory.create_batch(
            5, job=dependency.job)
        projectdependency = ProjectDependency.objects.create(
            project=project, dependency=dependency, auto_track=False,
            current_build=build5)

        table = get_build_table_for_project(project)

        self.assertEqual(
            [[dependency],
             [(build5, True)],
             [(build4, False)],
             [(build3, False)],
             [(build2, False)],
             [(build1, False)]], table)

from django.test import TestCase

from projects.models import (
    Project, DependencyType, Dependency, ProjectDependency)
from .factories import ProjectFactory, DependencyFactory
from jenkins.tests.factories import JobFactory, BuildFactory


class DependencyTypeTest(TestCase):

    def test_instantiation(self):
        """We can create DependencyTypes."""
        dependency_type = DependencyType.objects.create(
            name="my-test", config_xml="testing xml")


class DependencyTest(TestCase):

    def test_instantiation(self):
        """We can create Dependencies."""
        dependency_type = DependencyType.objects.create(
            name="my-test", config_xml="testing xml")
        dependency = Dependency.objects.create(
            name="My Dependency", dependency_type=dependency_type)


class ProjectDependencyTest(TestCase):

    def test_instantiation(self):
        """We can create ProjectDependency objects."""
        project = ProjectFactory.create()
        dependency = DependencyFactory.create()
        ProjectDependency.objects.create(
            project=project, dependency=dependency)
        self.assertEqual(
            set([dependency]), set(project.dependencies.all()))

    def test_auto_track_build(self):
        """
        If we create a new build for a dependency of a Project, and the
        ProjectDependency is set to auto_track then the current_build should be
        updated to reflect the new build.
        """
        build1 = BuildFactory.create()
        dependency = DependencyFactory.create(job=build1.job)

        project = ProjectFactory.create()
        project_dependency = ProjectDependency.objects.create(
            project=project, dependency=dependency)
        project_dependency.current_build = build1
        project_dependency.save()

        build2 = BuildFactory.create(job=build1.job)
        # Reload the project dependency
        project_dependency = ProjectDependency.objects.get(
            pk=project_dependency.pk)
        self.assertEqual(build2, project_dependency.current_build)

    def test_new_build_with_no_auto_track_build(self):
        """
        If we create a new build for a dependency of a Project, and the
        ProjectDependency is not set to auto_track then the current_build should
        not be updated.
        """
        build1 = BuildFactory.create()
        dependency = DependencyFactory.create(job=build1.job)

        project = ProjectFactory.create()
        project_dependency = ProjectDependency.objects.create(
            project=project, dependency=dependency, auto_track=False)
        project_dependency.current_build = build1
        project_dependency.save()

        build2 = BuildFactory.create(job=build1.job)
        # Reload the project dependency
        project_dependency = ProjectDependency.objects.get(
            pk=project_dependency.pk)
        self.assertEqual(build1, project_dependency.current_build)



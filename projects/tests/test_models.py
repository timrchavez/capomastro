from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from projects.models import (
    Project, Dependency, ProjectDependency, ProjectBuild,
    generate_projectbuild_id)
from .factories import (
    ProjectFactory, DependencyFactory, ProjectBuildFactory)
from jenkins.tests.factories import JobFactory, BuildFactory, ArtifactFactory


class DependencyTest(TestCase):

    def test_instantiation(self):
        """We can create Dependencies."""
        job = JobFactory.create()
        dependency = Dependency.objects.create(
            name="My Dependency", job=job)

    def test_get_current_build(self):
        """
        Dependency.get_current_build should return the most recent build that
        has completed and was SUCCESSful.
        """
        build1 = BuildFactory.create()
        build2 = BuildFactory.create(
            phase="FINISHED", status="SUCCESS", job=build1.job)
        dependency = DependencyFactory.create(job=build1.job)
        self.assertEqual(build2, dependency.get_current_build())

    def test_get_current_build_with_no_builds(self):
        """
        If there are no current builds for a given dependency, then we should
        get None.
        """
        dependency = DependencyFactory.create()
        self.assertEqual(None, dependency.get_current_build())


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


class ProjectTest(TestCase):

    def test_get_current_artifacts(self):
        """
        Project.get_current_artifacts returns the current set of artifacts
        for this project.
        """
        project = ProjectFactory.create()
        job = JobFactory.create()
        dependency = DependencyFactory.create(job=job)
        ProjectDependency.objects.create(
            project=project, dependency=dependency)
        build1 = BuildFactory.create(job=job)
        build2 = BuildFactory.create(job=job)

        artifact1 = ArtifactFactory.create(build=build1)
        artifact2 = ArtifactFactory.create(build=build2)

        self.assertEqual([artifact2], list(project.get_current_artifacts()))


class ProjectBuildTest(TestCase):

    def setUp(self):
        self.project = ProjectFactory.create()
        self.user = User.objects.create_user("testing")

    def test_generate_projectbuild_id(self):
        """
        generate_projectbuild_id should generate an id using the date and the
        sequence of builds on that date.

        e.g. 20140312.1 is the first build on the 12th March 2014
        """
        build1 = ProjectBuildFactory.create()
        expected_build_id = timezone.now().strftime("%Y%m%d.1")
        self.assertEqual(expected_build_id, generate_projectbuild_id(build1))
        build2 = ProjectBuildFactory.create(project=build1.project)
        expected_build_id = timezone.now().strftime("%Y%m%d.2")
        self.assertEqual(expected_build_id, generate_projectbuild_id(build2))

    def test_instantiation(self):
        """
        We can create ProjectBuilds.
        """
        projectbuild = ProjectBuild.objects.create(
            project=self.project, requested_by=self.user)
        self.assertEqual(self.user, projectbuild.requested_by)
        self.assertIsNotNone(projectbuild.requested_at)
        self.assertIsNone(projectbuild.ended_at)
        self.assertEqual("INCOMPLETE", projectbuild.status)

    def test_build_id(self):
        """
        When we create a project build, we should create a unique id for the
        build.
        """
        projectbuild = ProjectBuildFactory.create()
        expected_build_id = timezone.now().strftime("%Y%m%d.0")
        self.assertEqual(expected_build_id, projectbuild.build_id)

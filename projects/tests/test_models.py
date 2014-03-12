from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.utils import timezone

from projects.models import (
    Project, DependencyType, Dependency, ProjectDependency, ProjectBuild,
    generate_project_build_id)
from .factories import (
    ProjectFactory, DependencyFactory, DependencyTypeFactory, ProjectBuildFactory)
from jenkins.tests.factories import JobFactory, BuildFactory, ArtifactFactory


template_config = """
<?xml version='1.0' encoding='UTF-8'?>
<project><description>{{ dependency.description }}</description>
</project>"
"""


class DependencyTypeTest(TestCase):

    def test_instantiation(self):
        """We can create DependencyTypes."""
        dependency_type = DependencyType.objects.create(
            name="my-test", config_xml="testing xml")

    def test_generate_config_for_dependency(self):
        """
        We can use Django templating in the config.xml and this will be
        interpreted correctly.
        """
        dependency_type = DependencyTypeFactory.create(
            config_xml=template_config)
        dependency = DependencyFactory.create()
        job_xml = dependency_type.generate_config_for_dependency(dependency)
        self.assertIn(dependency.description, job_xml)

#    @override_settings(NOTIFICATION_HOST="http://example.com")
#    def test_generate_config_for_dependency_provides_notification_host(self):
#        """
#        """
#        dependency_type = DependencyTypeFactory.create(
#            config_xml="{{ notification_host }}")
#        dependency = DependencyFactory.create()
#        job_xml = dependency_type.generate_config_for_dependency(dependency)
#        self.assertEqual("http://example.com/jenkins/notifications/", job_xml)


class DependencyTest(TestCase):

    def test_instantiation(self):
        """We can create Dependencies."""
        dependency_type = DependencyType.objects.create(
            name="my-test", config_xml="testing xml")
        dependency = Dependency.objects.create(
            name="My Dependency", dependency_type=dependency_type)

    def test_get_current_build(self):
        """
        Dependency.get_current_build should return the most recent build that
        has completed and was SUCCESSful.
        """
        build1 = BuildFactory.create()
        build2 = BuildFactory.create(
            phase="FINISHED", result="SUCCESS", job=build1.job)
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

    def test_generate_project_build_id(self):
        """
        generate_project_build_id should generate an id using the date and the
        sequence of builds on that date.

        e.g. 20140312.1 is the first build on the 12th March 2014
        """
        build1 = ProjectBuildFactory.create()
        expected_build_id = timezone.now().strftime("%Y%m%d.1")
        self.assertEqual(expected_build_id, generate_project_build_id(build1))
        build2 = ProjectBuildFactory.create(project=build1.project)
        expected_build_id = timezone.now().strftime("%Y%m%d.2")
        self.assertEqual(expected_build_id, generate_project_build_id(build2))

    def test_instantiation(self):
        """
        We can create ProjectBuilds.
        """
        project_build = ProjectBuild.objects.create(
            project=self.project, requested_by=self.user)
        self.assertEqual(self.user, project_build.requested_by)
        self.assertIsNotNone(project_build.requested_at)
        self.assertIsNone(project_build.ended_at)
        self.assertEqual("INCOMPLETE", project_build.status)

    def test_build_id(self):
        """
        When we create a project build, we should create a unique id for the
        build.
        """
        project_build = ProjectBuildFactory.create()
        expected_build_id = timezone.now().strftime("%Y%m%d.0")
        self.assertEqual(expected_build_id, project_build.build_id)

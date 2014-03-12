import factory
from django.contrib.auth.models import User
from django.utils import timezone

from projects.models import Project, Dependency, DependencyType, ProjectBuild
from jenkins.tests.factories import JobFactory


class UserFactory(factory.DjangoModelFactory):
      FACTORY_FOR = User

      username = factory.Sequence(lambda n: "user%d" % n)
      email = factory.Sequence(lambda n: "test%d@example.com" % n)
      password = factory.PostGenerationMethodCall("set_password", "password")


class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project

    name = factory.Sequence(lambda n: "Project %d" % n)
    description = "This is a project."


class DependencyTypeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DependencyType

    name = factory.Sequence(lambda n: "type%d" % n)
    description = "This is a dependency type."
    config_xml = "<?xml version='1.0' encoding='UTF-8'?><project></project>"


class DependencyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Dependency

    dependency_type = factory.SubFactory(DependencyTypeFactory)
    name = factory.Sequence(lambda n: "Dependency %d" % n)
    job = factory.SubFactory(JobFactory)
    description = "This is a dependency."


class ProjectBuildFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ProjectBuild

    project = factory.SubFactory(ProjectFactory)
    requested_by = factory.SubFactory(UserFactory)
    requested_at = factory.LazyAttribute(lambda o: timezone.now())
    status = "INCOMPLETE"

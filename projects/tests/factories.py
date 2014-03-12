import factory

from projects.models import Project, Dependency, DependencyType
from jenkins.tests.factories import JobFactory


class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project

    name = factory.Sequence(lambda n: "Project %s" % n)
    description = "This is a project."


class DependencyTypeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DependencyType

    name = factory.Sequence(lambda n: "type%s" % n)
    description = "This is a dependency type."
    config_xml = "<?xml version='1.0' encoding='UTF-8'?><project></project>"


class DependencyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Dependency

    dependency_type = factory.SubFactory(DependencyTypeFactory)
    name = factory.Sequence(lambda n: "Dependency %s" % n)
    job = factory.SubFactory(JobFactory)
    description = "This is a dependency."

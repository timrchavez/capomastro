import factory
import factory.fuzzy

from jenkins.models import Build, Job, JenkinsServer, Artifact


class JenkinsServerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = JenkinsServer

    name = factory.Sequence(lambda n: "Server %s" % n)
    url = factory.Sequence(lambda n: "http://www%d.example.com/" % n)
    username = "root"
    password = "testing"
    remote_addr = "192.168.50.201"


class JobFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Job

    server = factory.SubFactory(JenkinsServerFactory)
    name = factory.Sequence(lambda n: "testjob%d" % n)


class BuildFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Build

    job = factory.SubFactory(JobFactory)
    build_id = factory.fuzzy.FuzzyText(length=12)
    number = factory.Sequence(lambda n: n)
    duration = factory.fuzzy.FuzzyInteger(100, 500000)
    result = "SUCCESS"
    phase = "STARTED"
    url = factory.Sequence(lambda n: "http://www.example.com/job/%d" % n)


class ArtifactFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Artifact

    build = factory.SubFactory(BuildFactory)
    filename = factory.fuzzy.FuzzyText(length=255)
    url = factory.Sequence(lambda n: "http://example.com/file/%d" % n)

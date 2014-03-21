import factory

from archives.models import Archive
from credentials.tests.factories import SshKeyPairFactory


class ArchiveFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Archive

    name = factory.Sequence(lambda n: "Archive %d" % n)
    host = "archive.example.com"
    policy = "cdimage"
    basedir = "/var/tmp"
    username = "testing"
    ssh_credentials = factory.SubFactory(SshKeyPairFactory)
    transport = "ssh"

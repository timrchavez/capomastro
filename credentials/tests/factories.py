import factory

from credentials.models import SshKeyPair


class SshKeyPairFactory(factory.DjangoModelFactory):
    FACTORY_FOR = SshKeyPair

    label = factory.Sequence(lambda n: "Keypair %d" % n)
    public_key = "THIS IS A DUMMY PUBLIC KEY"
    private_key = "THIS IS A DUMMY PRIVATE KEY"

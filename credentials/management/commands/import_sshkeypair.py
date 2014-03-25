from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from credentials.management.helpers import import_sshkeypair

class Command(BaseCommand):
    help = "Import ssh keypair"
    args = "[public key filename] [private key filename] [name]"

    option_list = BaseCommand.option_list + (
        make_option(
            "--update", action="store_true", dest="update",
            default=False, help="Update if label already exists."),
    )

    def handle(self, *args, **options):
        if len(args) != 3:
            raise CommandError(
                "must provide a label, public keyfile and private keyfile")
        label, public_key, private_key = args

        import_sshkeypair(
            label, public_key, private_key,
            update=options["update"], stdout=self.stdout)

        transaction.commit_unless_managed()

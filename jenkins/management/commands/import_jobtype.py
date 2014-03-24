import codecs
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from jenkins.management.helpers import import_jobtype


class Command(BaseCommand):
    help = "Import jobtype from config.xml"

    option_list = BaseCommand.option_list + (
        make_option(
            "--update", action="store_true", dest="update",
            default=False, help="Update if job name does not already exist."),
    )

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError("must provide a config.xml and job name")
        filename, job_name = args

        with codecs.open(filename) as f:
            import_jobtype(
                f, job_name, update=options["update"], stdout=self.stdout)

        transaction.commit_unless_managed()
